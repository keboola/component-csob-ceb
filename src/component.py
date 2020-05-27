import logging
import os
from datetime import datetime
import sys
import pytz
from kbc.env_handler import KBCEnvHandler

from ceb.client import Client
from ceb.parser import CEB_txt_parser

DEFAULT_TZ = 'Europe/Prague'

DEFAULT_CERT_FILE_NAME = 'cag.pem'
DEFAULT_FORMAT = 'TXT'
# default interval to wait between requests (s)
DEFAULT_RATELIMIT_INTERVAL = 0

PAR_CONTRACTNR = 'contract_nr'
PAR_SINCE_DATE = 'period_from'
PAR_CERT = '#cert'
PAR_TEST_SRV = 'test_service'
PAR_FORMAT = 'format'
KEY_RELATIVE_PERIOD = 'relative_period'
KEY_DEBUG = "debug"

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

PAR_FILE_TYPES = 'filetypes'
# [VYPIS, AVIZO, KURZY, IMPPROT]

MANDATORY_PARS = [PAR_CERT, PAR_CONTRACTNR]

APP_VERSION = '0.0.7'


class Component(KBCEnvHandler):

    def __init__(self, debug=False):
        KBCEnvHandler.__init__(self, MANDATORY_PARS, log_level=logging.DEBUG if debug else logging.INFO)
        # override debug from config
        if self.cfg_params.get(KEY_DEBUG):
            debug = True
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        logging.info('Loading configuration...')
        self._debug = debug

        try:
            self.validate_config(MANDATORY_PARS)
        except ValueError as e:
            logging.exception(e)
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
            since_date, to_dt = self.get_date_period_converted(params.get(KEY_RELATIVE_PERIOD),
                                                               params.get(KEY_RELATIVE_PERIOD))
        elif params.get(PAR_SINCE_DATE):
            since_date = datetime.strptime(params[PAR_SINCE_DATE], '%Y-%m-%d')
        else:
            since_date = None

        cert_path = os.path.join(self.data_path, 'crt', DEFAULT_CERT_FILE_NAME)
        # write cert to file
        if not os.path.exists(os.path.dirname(cert_path)):
            os.makedirs(os.path.dirname(cert_path))
        with open(cert_path, "w+", encoding="utf-8") as cert_file:
            cert_file.write(params[PAR_CERT])

        service_url = Client.TEST_SERVICE_URL if params.get(
            PAR_TEST_SRV) else Client.PRODUCTION_SERVICE_URL

        ceb_client = Client(params.get(
            PAR_CONTRACTNR), cert_path, base_url=service_url, debug=self._debug)

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

        # delete cert
        os.remove(cert_path)
        logging.info('Extraction finished!')


"""
        Main entrypoint
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_arg = sys.argv[1]
    else:
        debug_arg = False
    try:
        comp = Component(debug_arg)
        comp.run()
    except Exception as exc:
        logging.exception(exc)
        exit(1)
