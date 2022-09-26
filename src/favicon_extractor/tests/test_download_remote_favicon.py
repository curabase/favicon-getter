import unittest
from favicon_extractor import FavIcon, FavIconException
from io import BytesIO
from datauri import DataURI
from unittest.mock import patch
from magic import from_buffer
import os


DATA_URI = 'data:image/vnd.microsoft.icon;base64,AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAD///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B////Af///wEssQAPLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEApSyxAA////8B////Af///wEssQAPLLEAySyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDJLLEAD////wH///8BLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKX///8BLLEANyyxAP8ssQD/OLYP////////////////////////////////////////////LLEA/yyxAP8ssQD/LLEANyyxAJsssQD/LLEA/yyxAP8ssQD///////////8ssQD/LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxAJsssQDfLLEA/yyxAP8ssQD/LLEA////////////LLEA/yyxAP///////////yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEA+yyxAP8ssQD/LLEA/yyxAP///////////zKzB/8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEA+yyxAPsssQD/LLEA/zi2D///////////////////////////////////////LLEA/yyxAP8ssQD/LLEA/yyxAPsssQDfLLEA/yyxAP8ssQD/OLYP////////////LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEAmyyxAP8ssQD/LLEA/zKzB//9/v3///////7//v8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEAmyyxADcssQD/LLEA/yyxAP8ssQD/q+Ca//3+/f//////LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxADf///8BLLEApSyxAP8ssQD/LLEA/yyxAP8xswb/NLQK/yyxAP8vsgT/MLMF/yyxAP8ssQD/LLEA/yyxAKX///8B////ASyxAA8ssQDJLLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAMkssQAP////Af///wH///8BLLEADyyxAKUssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKUssQAP////Af///wH///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B+B8AAOAHAADAAwAAgAEAAIABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAAgAEAAMADAADgBwAA+B8AAA=='


class TestDownloadRemoteFavicon(unittest.TestCase):

    def setUp(self):
        self.favicon = FavIcon('http://example.com')

    def test_url_is_empty(self):
        url = ''
        with self.assertRaises(FavIconException):
            self.favicon.download_remote_favicon(url)

    def test_url_missing_http(self):
        url = '//example.com/favicon.ico'
        with self.assertRaises(FavIconException):
            self.favicon.download_remote_favicon(url)

    def test_url_is_malformed(self):
        urls = [
            'http:://example.com/favicon.ico',
            'http:///example.com/favicon.ico',
            'http//example.com/favicon.ico',
            'http:://e[[[xample.com/favicon.ico',
        ]
        for u in urls:
            url = u
            with self.assertRaises(FavIconException):
                self.favicon.download_remote_favicon(url)

    def test_url_is_valid_but_response_is_404(self):

        url = 'https://httpbin.org/status/404'

        # mock the response
        with self.assertRaises(FavIconException):
            self.favicon.download_remote_favicon(url)

    def test_url_is_valid_but_response_content_is_empty(self):

        url = 'http://example.com.com/favicon.ico'

        # mock the response
        with patch('requests.get') as m:
            m.return_value.content = b''
            m.return_value.status_code = 200
            with self.assertRaises(FavIconException):
                self.favicon.download_remote_favicon(url)

    def test_url_is_valid(self):
        url = 'http://example.com.com/favicon.ico'

        # mock the response
        with patch('requests.get') as m:
            content = DataURI(DATA_URI).data
            m.return_value.content = content
            m.return_value.status_code = 200
            image = self.favicon.download_remote_favicon(url)
            self.assertEqual(image, content)

    def test_svg_is_converted_properly(self):

        url = 'http://example.com.com/logo.svg'

        filename = '{}/fixtures/logo.svg'.format(os.path.dirname(os.path.realpath(__file__)))
        with open(filename,'rb') as f:
            content = f.read()

        with patch('requests.get') as m:
            m.return_value.content = content
            m.return_value.status_code = 200
            image = self.favicon.download_remote_favicon(url)
            self.assertIn(b'PNG', image)