import unittest
from ..favicon_extractor import find_in_html


class TestFaviconMethods(unittest.TestCase):

    """
    def test_has_no_favicon_defined_and_no_favicon_on_server(self):
        result = get_favicon('amazon.com')
    """
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


if __name__ == '__main__':
    unittest.main()
