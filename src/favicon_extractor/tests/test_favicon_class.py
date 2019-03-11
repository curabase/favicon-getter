from unittest import TestCase
from ..favicon_extractor import FavIcon, FavIconException
from io import BytesIO
from datauri import DataURI
from unittest.mock import patch
from magic import from_buffer
import os


class TestFavIconInstantiation(TestCase):

    def test_url_empty_is_null_or_empty(self):

        with self.assertRaises(FavIconException):
            FavIcon()

        with self.assertRaises(FavIconException):
            FavIcon('')

    def test_url_missing_domain(self):
        with self.assertRaises(FavIconException):
            FavIcon('google.com')

    def test_url_missing_scheme(self):
        with self.assertRaises(FavIconException):
            FavIcon('')

    def test_url_uses_ssh_scheme(self):

        f = FavIcon('ssh://user@host.com')
        self.assertTrue(f.presaved)

    def test_url_uses_localhost_scheme(self):

        f = FavIcon('http://localhost:8080')
        self.assertTrue(f.presaved)


class TestFavIconLogging(TestCase):

    def test_error_log_increments(self):
        f = FavIcon('http://google.com')
        f.log_error('test 123')
        self.assertTrue(len(f.errors) == 1)

class TestFavIconGetFavicon(TestCase):

    def setUp(self):
        self.base_dir = '/'.join([os.path.dirname(os.path.realpath(__file__)), 'fixtures'])

    def test_get_preexisting_icon(self):

        f = FavIcon('http://google.com', base_dir=self.base_dir)
        icon = f.get_favicon()
        self.assertTrue(f.presaved)
        self.assertIsInstance(icon, BytesIO)