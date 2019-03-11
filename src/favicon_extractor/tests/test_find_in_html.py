import unittest
from ..favicon_extractor import FavIcon, FavIconException

base_url = 'http://example.com'

NO_FAVICON_DEFINED = '''<!doctype html><head></head><body>this was from amazon.com</body></html>'''

FAVICON_AS_DATA_URI = '<link rel="shortcut icon" href="data:image/vnd.microsoft.icon;base64,AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAD///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B////Af///wEssQAPLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEApSyxAA////8B////Af///wEssQAPLLEAySyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDJLLEAD////wH///8BLLEApSyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKX///8BLLEANyyxAP8ssQD/OLYP////////////////////////////////////////////LLEA/yyxAP8ssQD/LLEANyyxAJsssQD/LLEA/yyxAP8ssQD///////////8ssQD/LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxAJsssQDfLLEA/yyxAP8ssQD/LLEA////////////LLEA/yyxAP///////////yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEA+yyxAP8ssQD/LLEA/yyxAP///////////zKzB/8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEA+yyxAPsssQD/LLEA/zi2D///////////////////////////////////////LLEA/yyxAP8ssQD/LLEA/yyxAPsssQDfLLEA/yyxAP8ssQD/OLYP////////////LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQDfLLEAmyyxAP8ssQD/LLEA/zKzB//9/v3///////7//v8ssQD///////////8ssQD/LLEA/yyxAP8ssQD/LLEAmyyxADcssQD/LLEA/yyxAP8ssQD/q+Ca//3+/f//////LLEA////////////LLEA/yyxAP8ssQD/LLEA/yyxADf///8BLLEApSyxAP8ssQD/LLEA/yyxAP8xswb/NLQK/yyxAP8vsgT/MLMF/yyxAP8ssQD/LLEA/yyxAKX///8B////ASyxAA8ssQDJLLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAMkssQAP////Af///wH///8BLLEADyyxAKUssQD/LLEA/yyxAP8ssQD/LLEA/yyxAP8ssQD/LLEA/yyxAKUssQAP////Af///wH///8B////Af///wH///8BLLEANyyxAJsssQDfLLEA+yyxAPsssQDfLLEAmyyxADf///8B////Af///wH///8B+B8AAOAHAADAAwAAgAEAAIABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAAgAEAAMADAADgBwAA+B8AAA==">'


class TestFindInHtml(unittest.TestCase):

    def setUp(self):
        self.favicon = FavIcon('http://example.com')

    def test_data_uri_in_href(self):
        url = self.favicon.find_in_html(FAVICON_AS_DATA_URI)
        self.assertTrue(url.startswith('data:image'))

    def test_no_favicon_defined(self):
        with self.assertRaises(FavIconException):
            self.favicon.find_in_html(NO_FAVICON_DEFINED)

    def test_find_in_html_slash_favicon(self):
        html = '<link rel="shortcut icon" href="/favicon.ico">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://example.com/favicon.ico')

    def test_uppercase_attribute_values(self):
        html = '<link rel="SHORTCUT ICON" href="//cdn.livetvcdn.net/favicon.ico">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://cdn.livetvcdn.net/favicon.ico')

    def test_lower_case_attribute_values(self):
        html = '<link rel="shortcut icon" href="//cdn.livetvcdn.net/favicon.ico">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://cdn.livetvcdn.net/favicon.ico')

    def test_mixed_case_attribute_values(self):
        html = '<link rel="Shortcut Icon" href="//cdn.livetvcdn.net/favicon.ico">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://cdn.livetvcdn.net/favicon.ico')

    def test_uppercase_tags(self):
        html = '<LINK REL="Shortcut Icon" HREF="//cdn.livetvcdn.net/favicon.ico">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://cdn.livetvcdn.net/favicon.ico')

    def test_mixed_case_tags(self):
        html = '<Link Rel="Shortcut Icon" Href="//cdn.livetvcdn.net/favicon.ico">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://cdn.livetvcdn.net/favicon.ico')

    def test_with_favicon_in_multiple_subfolders(self):
        html = '<link rel="shortcut icon" type="image/ico" href="/sites/all/themes/hedu2015/assets/img/favicon.ico" />'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://example.com/sites/all/themes/hedu2015/assets/img/favicon.ico')

    def test_svg_favicon(self):
        html = '<link rel="icon" href="https://resources.whatwg.org/logo.svg">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'https://resources.whatwg.org/logo.svg')

    def test_svg_favicon_relative_url(self):
        html = '<link rel="icon" href="/logo.svg">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://example.com/logo.svg')

    def test_apple_touch_icon(self):
        html = '<link rel="apple-touch-icon" sizes="152x152" href="/t/assets/icons/apple-touch-icon-152x152.png">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://example.com/t/assets/icons/apple-touch-icon-152x152.png')

    def test_apple_touch_icon_precomposed(self):
        html = '<link rel="apple-touch-icon-precomposed" href="/t/assets/icons/w-logo-orange.png">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://example.com/t/assets/icons/w-logo-orange.png')

    def test_multiple_finds(self):
        html = ('<link rel="apple-touch-icon" sizes="152x152" href="/t/assets/icons/apple-touch-icon-152x152.png">'
                '< link rel="apple-touch-icon-precomposed" href="/t/assets/icons/w-logo-orange.png" >'
                )
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://example.com/t/assets/icons/apple-touch-icon-152x152.png')

    def test_params_in_url(self):
        html = '<link href="/static/favicon.ico?v=2" rel="shortcut icon">'
        url = self.favicon.find_in_html(html)
        self.assertEqual(url, 'http://example.com/static/favicon.ico?v=2')
