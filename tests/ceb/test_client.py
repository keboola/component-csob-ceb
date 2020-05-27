import os
import unittest
from os.path import dirname
from unittest.mock import patch

from requests import Session, Response

from ceb.client import Client, ClientException


class TestClient(unittest.TestCase):

    @patch.object(Session, 'post')
    @patch("ceb.client.Client._CEB_SERVICE_WSDL",
           os.path.join(dirname(dirname(dirname(os.path.realpath(__file__)))), 'cebbc-wsdl',
                        'CEBBCWS.wsdl'))
    @patch("ceb.client.Client.MAX_RETRIES", 0)
    def test_503_response_invalid_xml_raises_client_exception(self, mock_post):
        mock_resp = Response()
        # set mock response
        mock_resp.status_code = 503
        mock_resp._content = 'TextResp'
        mock_resp.headers = {'Content-Type': 'text/xml'}
        mock_post.return_value = mock_resp

        cl = Client(1234, os.path.join(dirname(os.path.realpath(__file__)),
                                       'resources', 'cert.pem'), base_url='https://example.com', debug=True,
                    max_retries=0, rate_limit_interval=0)

        with self.assertRaises(ClientException) as er:
            cl.get_download_file_list()
        print(er.exception)


if __name__ == "__main__":
    unittest.main()
