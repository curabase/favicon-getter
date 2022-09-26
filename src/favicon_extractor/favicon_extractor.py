import logging
import os
import sys
import types
from io import BytesIO
from typing import List
from urllib.parse import urljoin, urlparse

import cairosvg
import requests
from bs4 import BeautifulSoup
from datauri import DataURI
from magic import from_buffer
from PIL import Image, ImageDraw, ImageFont


fmt = '%(asctime)s:%(levelname)s:favicon-{}:%(message)s'.format(
    os.getenv('IMAGE_VERSION'),
)
logging.basicConfig(format=fmt, stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


# TODO: check a random page to force a 404. Then try to pull favicon from here
#  heb.com is trying to block bots using JS on their homepage


HEADERS = types.MappingProxyType(
    {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) ' +
        'AppleWebKit/537.36 (KHTML, like Gecko) ' +
        'Chrome/48.0.2564.103 Safari/537.36',
    },
)
TIMEOUT = 10
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
LOCALHOSTS = ('127.0.0.1', 'localhost', '0.0.0.0')
HTML_ATTRIBUTES = (
    'apple-touch-icon',
    'apple-touch-icon-precomposed',
    'shortcut',
    'icon',
    'shortcut icon',
)
EXTENSIONS = ('ico', 'png')
SCHEMES_HTTP = ('http', 'https')
SCHEMES_NON_HTTP = ('ssh', 'telnet')


class FavIconException(Exception):
    pass


class FavIcon(object):

    errors: List = []

    def __init__(self, url: str = None, base_dir: str = None) -> None:
        """
        Initialize the FavIcon clss with a URL to get us started.

        :param url: String URL of the site you want to extract favicon
        :param base_dir: Optional base directory where files live
        """
        self.base_dir = base_dir if base_dir else BASE_DIR
        self.media_dir = '{0}/icons'.format(self.base_dir)

        if not url:
            raise FavIconException('url cannot be None')

        self.url = url
        self._process_meta()

        if not self.domain:
            raise FavIconException('Missing domain')

        if self.scheme in SCHEMES_NON_HTTP:
            self.filename = '{0}/assets/images/{1}.png'.format(self.base_dir, self.scheme)
        elif self.domain in LOCALHOSTS:
            self.filename = '{0}/assets/images/localhost.png'.format(self.base_dir)
        else:
            self.filename = '{0}/{1}.png'.format(self.media_dir, self.domain)

        # check if we already have the file
        self.presaved = os.path.isfile(self.filename)

    def _process_meta(self) -> None:
        """Parse the URL and set those parts as class variables."""
        url_parts = urlparse(self.url)
        self.scheme = url_parts.scheme.lower()
        self.domain = url_parts.netloc.split(':')[0].lower()
        self.base_url = '{0}://{1}'.format(self.scheme, url_parts.netloc)

    def download_remote_favicon(
        self,
        favicon_url: str,
        verify_ssl: bool = False,
    ) -> bytes:
        """
        Attempt to download the remote image.

        :param favicon_url: The target URL to download
        :param verify_ssl: Determine if we should validate SSL of server.
        :return: Bytes representation of the image
        """
        if favicon_url.startswith('data:image'):
            return DataURI(favicon_url).data

        try:
            # need to set headers here to fool sites like cafepress.com...
            h = requests.get(
                favicon_url,
                allow_redirects=True,
                timeout=TIMEOUT,
                headers=HEADERS,
                verify=verify_ssl,
            )
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.InvalidSchema,
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidURL,
        ) as e:
            raise FavIconException(e)

        try:
            h.raise_for_status()
        except requests.HTTPError:
            raise FavIconException(
                'HTTP Error on favicon url: {0}'.format(favicon_url),
            )

        if not h.content:
            raise FavIconException(
                'download_remove_favicon: ' +
                'Zero Length favicon: {0}'.format(favicon_url),
            )

        # is the returning file SVG?
        # If so, we have to convert it to bitmap (png)
        if 'SVG' in from_buffer(h.content) or favicon_url.endswith('.svg'):
            image = cairosvg.svg2png(bytestring=h.content)
        else:
            image = h.content

        if not is_bytes_valid_favicon(image):
            raise FavIconException(
                'Download_remove_favicon: Icon was ' +
                'not valid image: {0}'.format(favicon_url),
            )

        return image

    def log_error(self, message):
        """Log the errors."""
        log.debug(message)
        self.errors.append(message)

    def fetch_html(self, verify_ssl: bool = False) -> str:
        """
        Fetch the HTML from a webpage.

        :param verify_ssl: boolean verify_ssl
        :return: HTML body of the response
        """
        try:
            # set the user agent to fool economist.com and other sites who care.
            r = requests.get(
                self.url,
                timeout=TIMEOUT,
                headers=HEADERS,
                verify=verify_ssl,
            )

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as e:
            raise FavIconException(e)

        # if we were redirected off the domain, then we catch it here
        new_domain_parts = urlparse(r.url)
        new_domain = new_domain_parts.netloc.split(':')[0].lower()

        # now we just re-check favicons on the new domain
        if self.domain != new_domain:
            log.debug(
                'Switching domains. {0} -> {1}'.format(
                    self.domain, new_domain,
                ),
            )
            self.url = r.url
            self._process_meta()

        return r.text

    def find_in_html(self, html: str) -> str:
        """
        Look for a favicon (or apple touch icon) in html strings.

        :param html: The HTML string (often entire page source)
        :return: a string URL of the favicon location or data-uri
        """
        soup = BeautifulSoup(html, 'html5lib')

        # find the first available link to an icon we can download
        target = soup.find(
            'link',
            attrs={'rel': lambda x: x.lower() in HTML_ATTRIBUTES},
        )

        if not target:
            raise FavIconException(
                'Could not find suitable link for favicon extraction',
            )

        href = target.get('href', '')

        return self.calc_href(href)

    def calc_href(self, href: str = None) -> str:
        """
        Calculate the complete URL based on the base_url and the href fragment.

        :param href: String representation of the url/link.
        :return:
        """

        if not href:
            raise FavIconException('href is required as param')

        # for those clever devs who pack the favicon as a data uri
        if href.startswith('data:image'):
            return href

        if href.startswith('http'):
            return href

        if href.startswith('//'):
            return 'http:{0}'.format(href)

        return urljoin(self.base_url, href)

    def get_favicon(self) -> BytesIO:
        """
        Return bytes.

        :return: Bytes of image (BytesIO)
        """
        if self.presaved:
            with open(self.filename, 'rb') as f:
                image = f.read()

            return BytesIO(image)

        try:
            html = self.fetch_html()
        except FavIconException as e:
            self.log_error(e)
            image = make_image(self.domain)
            return BytesIO(image)

        try:
            favicon_url = self.find_in_html(html)
        except FavIconException as e:
            self.log_error(e)
            favicon_url = '{0}/favicon.ico'.format(self.base_url)

        try:
            raw_image = self.download_remote_favicon(favicon_url)
        except FavIconException as e:
            self.log_error(e)
            image = make_image(self.domain)
        else:
            image = resize_image(raw_image)

        with open(self.filename, 'wb') as f:
            f.write(image)

        # wrap data in BytesIO and send it out
        return BytesIO(image)


def common_locations(domain: str) -> List[str]:
    """
    Produce a list of the most common locations where we might find a favicon.

    :param domain: just the base domain name (example.com)
    :return: a list of urls
    """
    # extensions = ['ico','png','gif','jpg','jpeg']
    subdomains = ['']
    locations = []

    # check in 20 possible places
    # this is probably a bit excessive
    for ext in EXTENSIONS:
        for scheme in SCHEMES_HTTP:
            for subdomain in subdomains:
                url = f'{scheme}://{subdomain}{domain}/favicon.{ext}'
                locations.append(url)

    return locations


def make_image(domain: str) -> bytes:
    """
    Given a domain name, generate a favicon that is just the first letter.

    :param domain:
    :return:
    """
    letter = domain[0].upper()

    font = ImageFont.truetype(
        '{0}/assets/fonts/DejaVuSansMono-webfont.ttf'.format(BASE_DIR),
        24,
    )
    img = Image.new('RGBA', (32, 32), (128, 128, 128))
    draw = ImageDraw.Draw(img)
    color = (255, 255, 255)
    draw.text((8, 1), letter, color, font=font)

    out = BytesIO()

    img.save(out, 'png')
    return out.getvalue()


def resize_image(image: bytes, width: int = 16, height: int = 16) -> bytes:
    """
    Resize an image made of bytes.

    :param image: The image (bytes)
    :param width: Desired width in pixels
    :param height: Desired height in pixels
    :return: Image in Bytes
    """
    img = Image.open(BytesIO(image))
    img = img.convert('RGB') if img.mode == 'CMYK' else img

    img.thumbnail((width, height), Image.Resampling.LANCZOS)

    out = BytesIO()
    img.save(out, 'png')
    return out.getvalue()


def is_bytes_valid_favicon(img_data: bytes) -> bool:
    """
    Check if the bytes are valid icons.

    :param img_data: Bytes object with image date
    :return: Boolean / yes it is a valid icon. No otherwise.
    """
    file_bytes = BytesIO(img_data)
    the_magic = from_buffer(file_bytes.read())
    file_types = ('icon', 'PNG', 'GIF', 'JPEG', 'SVG', 'PC bitmap')

    if any([ftype in the_magic for ftype in file_types]):
        return True

    # TODO: detect if all pixels are white or transparent
    # http://stackoverflow.com/a/1963146/1646663
    # http://stackoverflow.com/a/14041871/1646663

    return False
