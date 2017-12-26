import unittest
from ..favicon_extractor import calc_href

base_url = 'http://example.com'
expected = 'http://example.com/favicon.ico'

# format is base_url, href, expected output
inputs = [

    (base_url, 'http://example.com/favicon.ico', expected),
    (base_url, '//example.com/favicon.ico', expected),
    (base_url, '/favicon.ico', expected),
    (base_url, 'https://example.com/favicon.ico', 'https://example.com/favicon.ico'),
    ('https://example.com', 'http://example.com/favicon.ico', 'http://example.com/favicon.ico'),
]


class TestCalcHref(unittest.TestCase):

    def test_calc_href(self):
        for i in inputs:
            this_url, href, expected_output = i
            self.assertEqual(calc_href(href, this_url), expected_output)


if __name__ == '__main__':
    unittest.main()
