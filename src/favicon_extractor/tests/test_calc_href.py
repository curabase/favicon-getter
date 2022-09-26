import unittest
from favicon_extractor import FavIcon

base_url = 'http://example.com'
expected = 'http://example.com/favicon.ico'

# format is base_url, href, expected output
inputs = [

    ('http://example.com/favicon.ico', expected),
    ('//example.com/favicon.ico', expected),
    ('/favicon.ico', expected),
    ('https://example.com/favicon.ico', 'https://example.com/favicon.ico'),
    ('http://example.com/favicon.ico', 'http://example.com/favicon.ico'),
    ('/sites/all/themes/hedu2015/assets/img/favicon.ico','http://example.com/sites/all/themes/hedu2015/assets/img/favicon.ico')
]


class TestCalcHref(unittest.TestCase):

    def test_calc_href(self):

        f = FavIcon('http://example.com')
        for (href, expected_output) in inputs:
            self.assertEqual(f.calc_href(href), expected_output)
