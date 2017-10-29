import unittest

"""
from fixtures import *
"""
from .favicon_extractor import find_in_html


class TestFaviconMethods(unittest.TestCase):

    """
    def test_has_no_favicon_defined_and_no_favicon_on_server(self):
        result = get_favicon('amazon.com')
    """
    def test_check_dns(self):
        pass

    def test_calc_href(self):
        pass

    def test_poke_url_timesout(self):
        pass

    def test_poke_url_finds_favicon(self):
        pass

    def test_poke_url_does_not_find_favicon(self):
        pass

    def test_find_in_html_slash_favicon(self):
        html = '<link rel="shortcut icon" href="/favicon.ico">'
        self.assertEqual(find_in_html(html, 'boom.com'),
                         'http://boom.com/favicon.ico')

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')


if __name__ == '__main__':
    unittest.main()
