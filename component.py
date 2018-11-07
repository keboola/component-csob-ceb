from datetime import datetime
from kbc.env_handler import KBCEnvHandler
from ceb.parser import CEB_txt_parser
from ceb.client import Client

import logging
import pytz
import os

DEFAULT_TZ = 'Europe/Prague'

DEFAULT_CERT_PATH = './cert/cag.pem'
DEFAULT_FORMAT = 'TXT'
# default interval to wait between requests (s)
DEFAULT_RATELIMIT_INTERVAL = 60

PAR_CONTRACTNR = 'contract_nr'
PAR_SINCE_DATE = 'period_from'
PAR_CERT = '#cert'
PAR_TEST_SRV = 'test_service'
PAR_FORMAT = 'format'
KEY_RELATIVE_PERIOD = 'relative_period'

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

PAR_FILE_TYPES = 'filetypes'
# [VYPIS, AVIZO, KURZY, IMPPROT]

MANDATORY_PARS = [PAR_CERT, PAR_CONTRACTNR]

APP_VERSION = '0.0.1'


class Component(KBCEnvHandler):

    def __init__(self, debug=True):
        KBCEnvHandler.__init__(self, MANDATORY_PARS)
        # override debug from config
        if(debug or self.cfg_params.get('debug')):
            debug = True
            self._debug = True
        else:
            self._debug = False

        self.set_default_logger('DEBUG' if debug else 'INFO')
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

        try:
            self.validateConfig()
        except ValueError as e:
            logging.error(e)
            exit(1)

    def run(self, debug=True):
        '''
        Main execution code
        '''
        params = self.cfg_params

        state_file = self.get_state_file()
        if state_file and state_file.get('prev_run') and params.get('since_last'):
            since_date = state_file.get('prev_run')
        elif self.cfg_params.get(KEY_RELATIVE_PERIOD):
            since_date = super().get_past_date(self.cfg_params.get(KEY_RELATIVE_PERIOD))
        elif params.get(PAR_SINCE_DATE):
            since_date = datetime.strptime(params[PAR_SINCE_DATE], '%Y-%m-%d')
        else:
            since_date = None

        # write cert to file
        if not os.path.exists(os.path.dirname(DEFAULT_CERT_PATH)):
            os.makedirs(os.path.dirname(DEFAULT_CERT_PATH))
        with open(DEFAULT_CERT_PATH, "w+", encoding="utf-8") as cert_file:
            cert_file.write(params[PAR_CERT])

        service_url = Client.TEST_SERVICE_URL if params.get(
            PAR_TEST_SRV) else Client.PRODUCTION_SERVICE_URL

        ceb_client = Client(params.get(
            PAR_CONTRACTNR), DEFAULT_CERT_PATH, base_url=service_url, debug=self._debug)

        now_dt = datetime.now(pytz.timezone(DEFAULT_TZ))

        # support only vypis
        file_types = ['VYPIS']  # params.get(PAR_FILE_TYPES)

        res_files = ceb_client.download_all_files(since_date, now_dt, os.path.join(self.data_path, 'tmp'), file_types,
                                                  DEFAULT_FORMAT)

        if not res_files:
            logging.info('No files downloaded!')

        # parse results
        res_folders = {}
        for res in res_files:
            parsed_res = CEB_txt_parser.parse(
                res['file_path'], self.tables_out_path, res['type'])

            for f in parsed_res:
                res_folders[f['type']] = f['id']

        for folder in res_folders:
            self.create_sliced_tables(
                folder_name=folder, pkey=res_folders[folder], incremental=True, src_delimiter=",", src_enclosure='"')

        logging.info('Extraction finished!')


"""
        Main entrypoint
"""
if __name__ == "__main__":
    comp = Component()
    comp.run()
