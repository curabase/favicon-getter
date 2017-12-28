import unittest
from ..favicon_extractor import download_remote_favicon
from io import BytesIO
from datauri import DataURI
from unittest.mock import patch
from magic import from_buffer
import os


DATA_URI = 'data:image/vnd.microsoft.icon;base64,AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAD///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B////Af///wEssQAPLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEApSyxAA////8B////Af///wEssQAPLLEAySyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDJLLEAD////wH///8BLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKX///8BLLEANyyxAP8ssQD/OLYP////////////////////////////////////////////LLEA/yyxAP8ssQD/LLEANyyxAJsssQD/LLEA/yyxAP8ssQD///////////8ssQD/LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxAJsssQDfLLEA/yyxAP8ssQD/LLEA////////////LLEA/yyxAP///////////yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEA+yyxAP8ssQD/LLEA/yyxAP///////////zKzB/8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEA+yyxAPsssQD/LLEA/zi2D///////////////////////////////////////LLEA/yyxAP8ssQD/LLEA/yyxAPsssQDfLLEA/yyxAP8ssQD/OLYP////////////LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEAmyyxAP8ssQD/LLEA/zKzB//9/v3///////7//v8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEAmyyxADcssQD/LLEA/yyxAP8ssQD/q+Ca//3+/f//////LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxADf///8BLLEApSyxAP8ssQD/LLEA/yyxAP8xswb/NLQK/yyxAP8vsgT/MLMF/yyxAP8ssQD/LLEA/yyxAKX///8B////ASyxAA8ssQDJLLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAMkssQAP////Af///wH///8BLLEADyyxAKUssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKUssQAP////Af///wH///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B+B8AAOAHAADAAwAAgAEAAIABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAAgAEAAMADAADgBwAA+B8AAA=='


class TestDownloadRemoteFavicon(unittest.TestCase):

    def test_url_is_empty(self):
        self.assertRaises(ValueError, download_remote_favicon,'')

    def test_url_missing_http(self):
        self.assertRaises(ValueError, download_remote_favicon,'//example.com/favicon.ico')

    def test_url_is_malformed(self):
        self.assertFalse(download_remote_favicon('http:://example.com/favicon.ico'))
        self.assertFalse(download_remote_favicon('http:///example.com/favicon.ico'))
        self.assertFalse(download_remote_favicon('http//example.com/favicon.ico'))
        self.assertFalse(download_remote_favicon('http:://e[[[xample.com/favicon.ico'))

    def test_url_is_valid_but_response_is_404(self):

        # mock the response
        with patch('requests.get') as m:
            m.return_value.content = None
            m.return_value.status_code = 404
            self.assertFalse(download_remote_favicon('http://example.com.com/favicon.ico'))

    def test_url_is_valid_but_response_content_is_empty(self):

        # mock the response
        with patch('requests.get') as m:
            m.return_value.content = b''
            m.return_value.status_code = 200
            self.assertFalse(download_remote_favicon('http://example.com.com/favicon.ico'))

    def test_url_is_valid(self):
        content = BytesIO(DataURI(DATA_URI).data)

        # mock the response
        with patch('requests.get') as m:
            content = BytesIO(DataURI(DATA_URI).data).read()
            m.return_value.content = content
            m.return_value.status_code = 200
            self.assertEqual(download_remote_favicon('http://example.com.com/favicon.ico'), content)

    def test_svg_is_converted_properly(self):
        filename = '{}/fixtures/logo.svg'.format(os.path.dirname(os.path.realpath(__file__)))
        with open(filename,'rb') as f:
            content = f.read()

        with patch('requests.get') as m:
            m.return_value.content = content
            m.return_value.status_code = 200

            result = from_buffer(download_remote_favicon('http://whatwg.org/favicon.svg'))
            self.assertIn('PNG', result)


if __name__ == '__main__':
    unittest.main()
