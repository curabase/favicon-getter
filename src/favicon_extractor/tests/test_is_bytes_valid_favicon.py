import unittest
from favicon_extractor.favicon_extractor import is_bytes_valid_favicon
from io import BytesIO
from datauri import DataURI
import os


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_URI = 'data:image/vnd.microsoft.icon;base64,AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAD///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B////Af///wEssQAPLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEApSyxAA////8B////Af///wEssQAPLLEAySyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDJLLEAD////wH///8BLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKX///8BLLEANyyxAP8ssQD/OLYP////////////////////////////////////////////LLEA/yyxAP8ssQD/LLEANyyxAJsssQD/LLEA/yyxAP8ssQD///////////8ssQD/LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxAJsssQDfLLEA/yyxAP8ssQD/LLEA////////////LLEA/yyxAP///////////yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEA+yyxAP8ssQD/LLEA/yyxAP///////////zKzB/8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEA+yyxAPsssQD/LLEA/zi2D///////////////////////////////////////LLEA/yyxAP8ssQD/LLEA/yyxAPsssQDfLLEA/yyxAP8ssQD/OLYP////////////LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEAmyyxAP8ssQD/LLEA/zKzB//9/v3///////7//v8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEAmyyxADcssQD/LLEA/yyxAP8ssQD/q+Ca//3+/f//////LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxADf///8BLLEApSyxAP8ssQD/LLEA/yyxAP8xswb/NLQK/yyxAP8vsgT/MLMF/yyxAP8ssQD/LLEA/yyxAKX///8B////ASyxAA8ssQDJLLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAMkssQAP////Af///wH///8BLLEADyyxAKUssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKUssQAP////Af///wH///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B+B8AAOAHAADAAwAAgAEAAIABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAAgAEAAMADAADgBwAA+B8AAA=='


class TestIsBytesValidFavicon(unittest.TestCase):

    def setUp(self):
        pass

    def test_data_not_type_bytesio(self):

        with self.assertRaises(TypeError):
            is_bytes_valid_favicon()


    def test_data_uri_is_valid(self):
        data = DataURI(DATA_URI).data
        self.assertTrue(is_bytes_valid_favicon(data))

    def test_empty_file_is_invalid(self):
        with open(f'{BASE_DIR}/fixtures/invalid_favicon_empty_file.png', 'rb') as f:
            data = f.read()
        self.assertFalse(is_bytes_valid_favicon(data))
