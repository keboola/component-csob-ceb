'''
Created on 28. 9. 2018

@author: esner
'''

import logging.config
import os
import time
from timeit import default_timer as timer

import requests
import zeep
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from zeep import helpers
from zeep.transports import Transport


class ClientException(Exception):
    '''
    Exc
    '''


class Client:
    MAX_RETRIES = 10
    _CEB_SERVICE_WSDL = '../cebbc-wsdl/CEBBCWS.wsdl'

    PRODUCTION_SERVICE_URL = 'ceb-bc.csob.cz'
    TEST_SERVICE_URL = 'testceb-bc.csob.cz'
    # Constants, keys
    _KEY_FILENAME = 'Filename'
    _KEY_FILELIST = 'FileList'
    _KEY_STATUS = 'Status'
    _KEY_FILEDETAIL = 'FileDetail'
    _KEY_TYPE = 'Type'

    def __init__(self, contract_number, cert_path, base_url=PRODUCTION_SERVICE_URL,
                 rate_limit_interval=60, operation_timeout=3600, debug=False, max_retries=MAX_RETRIES,
                 backoff_factor=0.3):

        # final variables setup
        self._rate_limit_interval = rate_limit_interval
        self._operation_timeout = operation_timeout

        self.contract_number = contract_number
        self.cert = cert_path
        self._auth_header = {'User-Agent': 'GD wr api client'}

        self._set_logger(debug)

        session = Session()
        retry = Retry(
            total=max_retries,
            read=max_retries,
            connect=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(500, 501, 502, 503, 504),
            method_whitelist=('GET', 'POST', 'PATCH', 'UPDATE')
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.cert = cert_path
        transport = Transport(session=session)

        # # create SOAP client
        self.client = zeep.Client(self._CEB_SERVICE_WSDL, transport=transport)
        # # setup service using base url
        self.client_service = self._get_service(self.client, base_url)

    def _set_logger(self, debug):
        if debug:
            log_level = "DEBUG"
        else:
            log_level = "INFO"

        logging.config.dictConfig({
            'version': 1,
            'formatters': {
                'verbose': {
                    'format': '%(name)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose',
                },
            },
            'loggers': {
                'zeep.transports': {
                    'level': log_level,
                    'propagate': True,
                    'handlers': ['console'],
                },
            }
        })

    def _http_get(self, url, params=None, **kwargs):
        """
        Construct a requests GET call with args and kwargs and process the
        results.


        Args:
            url (str): requested url
            params (dict): additional url params to be passed to the underlying
                requests.get
            **kwargs: Key word arguments to pass to the get requests.get

        Returns:
            r (requests.Response): object

        Raises:
            requests.HTTPError: If the API request fails.
        """
        headers = kwargs.pop('headers', {})
        headers.update(self._auth_header)
        r = requests.get(url, params, headers=headers,
                         cert=self.cert, **kwargs)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            # Handle different error codes
            raise
        else:
            return r

    def _get_service(self, client, base_url):
        service_binding = client.service._binding.name
        service_address = client.service._binding_options['address']
        return client.create_service(service_binding, service_address.replace('${BankAdress}', base_url))

    def _try_request(self, client_call, retries, **args):
        """
        Wrapper function that should be called for all client requests. Ensures the rate-limit is not exceeded.
        Handles retries on exception.

        client_call -- function to execute (Lambda)
        retries -- number of retries on failure
        """
        success = False
        attempts = 0
        # wait to make sure ratelimit is not exceeded
        while not success:
            time.sleep(self._rate_limit_interval)
            try:
                attempts += 1
                res = client_call()
                success = True
            except zeep.exceptions.Error as ex:
                if attempts <= retries:
                    success = False
                else:
                    raise ClientException(ex.message) from ex
            except requests.exceptions.SSLError as ser:
                raise ClientException("SSL connection failed, check your certificate / pkey!") from ser

        return res

    def get_download_file_list(self, prev_query_timestamp=None, created_after=None,
                               created_before=None, file_types=None):
        """
        prev_query_timestamp -- datetime specifying moment since to search
                                for new files (max 45 days back) [datetime.date]
        created_after -- just files created afer datetime.date
        file_types -- file type [VYPIS, AVIZO, KURZY, IMPPROT]

        """
        # build filetypes list
        file_type_list = None
        if file_types:
            file_type_list = []
            for type_ in file_types:
                file_type_list.append({"FileType": type_})

        filter_ = {"FileTypes": file_type_list,
                   "CreatedAfter": created_after,
                   "CreatedBefore": created_before}
        res = self._try_request(lambda: self.client_service.
                                GetDownloadFileList_v2(ContractNumber=self.contract_number,
                                                       PrevQueryTimestamp=prev_query_timestamp,
                                                       Filter=filter_), retries=self.MAX_RETRIES)

        file_list = helpers.serialize_object(res)
        return file_list

    def _all_files_ready(self, files):
        return all(file.get(self._KEY_STATUS) == "D" for file in files)

    def _get_unfinished_files_strings(self, files):
        return [str(file) for file in files if file.get(self._KEY_STATUS) != "D"]

    def _filter_file_types(self, file_list, file_types, format_):
        if not file_list or not file_list.get(self._KEY_FILEDETAIL):
            return []

        file_details = []
        details_dict = file_list.get(self._KEY_FILEDETAIL)
        file_details.extend([detail for detail in details_dict
                             if detail.get(self._KEY_TYPE) in file_types
                             and detail.get(self._KEY_FILENAME).endswith('.' + format_)])
        return file_details

    def _download_files_by_type(self, files, destination_folder):
        """
        Downloads files into new directiories in destination_folder based on their type.
        e.g. destination_folder/VYPIS/vypis.txt

        files -- OrderedDictionary object containing FileDetail object from response

        returns list of dicts {'file_path':f.name,
                                 'type' : type}

        """
        result_files = []
        for file in files:
            f = self.download_file(file.get('Url'), os.path.join(
                destination_folder, file.get(self._KEY_FILENAME).replace(":", "_")))
            result_files.extend([{'file_path': f.name,
                                  'type': file.get(self._KEY_TYPE)}])

        return result_files

    def download_all_files(self, created_date, until_date, result_folder_path, file_types, format_='TXT'):
        """
        Download all statement files into result_folder_path/TYPE/FILE_NAME.

        created_date -- files created after
        until_date -- files created before
        file_types -- ['VYPIS', 'AVIZO' ...]

        Returns list of downloaded files
        """

        start = timer()
        continue_ = True
        while continue_ and timer() - start < self._operation_timeout:
            files = self.get_download_file_list(
                created_after=created_date, created_before=until_date, file_types=file_types)

            files = self._filter_file_types(
                files.get(self._KEY_FILELIST), file_types, format_)

            files_ready = self._all_files_ready(files)
            if files_ready:
                continue_ = False

        if not files_ready:
            raise TimeoutError('Some of the files: [{}] failed to be prepared for download in time.'.format(
                ''.join(self._get_unfinished_files_strings(files))))

        result_files = self._download_files_by_type(files, result_folder_path)

        return result_files

    def download_file(self, url, destination_path):
        cleaned_path = destination_path.replace(" ", "")
        print(cleaned_path)
        r = self._http_get(url)
        os.makedirs(os.path.dirname(cleaned_path), exist_ok=True)
        with open(cleaned_path, 'wb+') as f:
            f.write(r.content)
            f.close()
        return f
