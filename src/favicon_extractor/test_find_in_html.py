import unittest
from .favicon_extractor import find_in_html

base_url = 'http://example.com'

NO_FAVICON_DEFINED = '''<!doctype html><head></head><body>this was from amazon.com</body></html>'''

FAVICON_AS_DATA_URI = '<link rel="shortcut icon" href="data:image/vnd.microsoft.icon;base64,AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAD///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B////Af///wEssQAPLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEApSyxAA////8B////Af///wEssQAPLLEAySyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDJLLEAD////wH///8BLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKX///8BLLEANyyxAP8ssQD/OLYP////////////////////////////////////////////LLEA/yyxAP8ssQD/LLEANyyxAJsssQD/LLEA/yyxAP8ssQD///////////8ssQD/LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxAJsssQDfLLEA/yyxAP8ssQD/LLEA////////////LLEA/yyxAP///////////yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEA+yyxAP8ssQD/LLEA/yyxAP///////////zKzB/8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEA+yyxAPsssQD/LLEA/zi2D///////////////////////////////////////LLEA/yyxAP8ssQD/LLEA/yyxAPsssQDfLLEA/yyxAP8ssQD/OLYP////////////LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEAmyyxAP8ssQD/LLEA/zKzB//9/v3///////7//v8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEAmyyxADcssQD/LLEA/yyxAP8ssQD/q+Ca//3+/f//////LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxADf///8BLLEApSyxAP8ssQD/LLEA/yyxAP8xswb/NLQK/yyxAP8vsgT/MLMF/yyxAP8ssQD/LLEA/yyxAKX///8B////ASyxAA8ssQDJLLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAMkssQAP////Af///wH///8BLLEADyyxAKUssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKUssQAP////Af///wH///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B+B8AAOAHAADAAwAAgAEAAIABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAAgAEAAMADAADgBwAA+B8AAA==">'


class TestFindInHtml(unittest.TestCase):

    def test_data_uri_in_href(self):
        self.assertTrue(find_in_html(FAVICON_AS_DATA_URI, base_url).startswith('data:image'))

    def test_no_favicon_defined(self):
        self.assertEqual(find_in_html(NO_FAVICON_DEFINED, base_url), 'missing')

    def test_find_in_html_slash_favicon(self):
        html = '<link rel="shortcut icon" href="/favicon.ico">'
        self.assertEqual(find_in_html(html, 'http://boom.com'),
                         'http://boom.com/favicon.ico')

    def test_uppercase_attribute_values(self):
        html = '<link rel="SHORTCUT ICON" href="//cdn.livetvcdn.net/favicon.ico">'
        self.assertEqual(find_in_html(html, 'boom.com'),
                         'http://cdn.livetvcdn.net/favicon.ico')

    def test_lower_case_attribute_values(self):
        html = '<link rel="shortcut icon" href="//cdn.livetvcdn.net/favicon.ico">'
        self.assertEqual(find_in_html(html, 'boom.com'),
                         'http://cdn.livetvcdn.net/favicon.ico')

    def test_mixed_case_attribute_values(self):
        html = '<link rel="Shortcut Icon" href="//cdn.livetvcdn.net/favicon.ico">'
        self.assertEqual(find_in_html(html, 'boom.com'),
                         'http://cdn.livetvcdn.net/favicon.ico')

    def test_uppercase_tags(self):
        html = '<LINK REL="Shortcut Icon" HREF="//cdn.livetvcdn.net/favicon.ico">'
        self.assertEqual(find_in_html(html, 'boom.com'),
                         'http://cdn.livetvcdn.net/favicon.ico')

    def test_mixed_case_tags(self):
        html = '<Link Rel="Shortcut Icon" Href="//cdn.livetvcdn.net/favicon.ico">'
        self.assertEqual(find_in_html(html, 'boom.com'),
                         'http://cdn.livetvcdn.net/favicon.ico')

if __name__ == '__main__':
    unittest.main()
