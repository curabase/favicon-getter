import unittest

from fixtures import *
from favicon_extractor import get_favicon

class TestFaviconMethods(unittest.TestCase):

    def test_has_no_favicon_defined_and_no_favicon_on_server(self):
        result = get_favicon('amazon.com')


    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

if __name__ == '__main__':
    unittest.main()
