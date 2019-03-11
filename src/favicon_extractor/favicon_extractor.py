import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datauri import DataURI
from PIL import Image, ImageDraw, ImageFont
import cairosvg
from io import BytesIO

from magic import from_buffer
import os, sys
import logging

from typing import Union, List

from requests import HTTPError


fmt = '%(asctime)s:%(levelname)s:favicon-{}:%(message)s'.format(os.getenv('IMAGE_VERSION'))
logging.basicConfig(format=fmt, stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

"""
TODO: check a random page to force a 404. Then try to pull favicon from here
      heb.com is trying to block bots using JS on their homepage
"""

HEADERS = {
    'User-agent': ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/48.0.2564.103 Safari/537.36")
}
TIMEOUT = 10
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class FavIconException(Exception):
    pass


class FavIcon(object):

    HEADERS = {
        'User-agent': ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/48.0.2564.103 Safari/537.36")
    }

    TIMEOUT = 10
    LOCALHOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']
    SCHEMES = ['ssh', 'telnet']
    HTML_ATTRIBUTES = ['apple-touch-icon', 'apple-touch-icon-precomposed', 'shortcut', 'icon', 'shortcut icon']

    errors:List = []
    presaved:bool = False


    def __init__(self, url:str = None, base_dir:str = None):
        """

        :param url:
        :param base_dir:
        """

        self.base_dir = base_dir if base_dir else os.path.dirname(os.path.realpath(__file__))
        self.media_dir = f'{self.base_dir}/icons'

        if not url:
            raise FavIconException('url cannot be None')

        self.url = url
        self._process_meta()

        if len(self.domain) == 0:
            raise FavIconException('Missing domain')

        if self.scheme in self.SCHEMES:
            b = os.path.dirname(os.path.realpath(__file__))
            self.filename = f"{b}/assets/images/{self.scheme}.png"
        elif self.domain in self.LOCALHOSTS:
            b = os.path.dirname(os.path.realpath(__file__))
            self.filename = f"{b}/assets/images/localhost.png"
        else:
            self.filename = f"{self.media_dir}/{self.domain}.png"

        # check if we already have the file
        if os.path.isfile(self.filename):
            self.presaved = True

    def _process_meta(self):
        url_parts = urlparse(self.url)
        self.scheme = url_parts.scheme.lower()
        self.domain = url_parts.netloc.split(':')[0].lower()
        self.base_url = f"{self.scheme}://{url_parts.netloc}"



    def download_remote_favicon(self, favicon_url: str) -> bytes:

        if favicon_url.startswith('data:image'):
            return DataURI(favicon_url).data

        try:
            # need to set headers here to fool sites like cafepress.com...
            h = requests.get(favicon_url, allow_redirects=True, timeout=TIMEOUT, headers=HEADERS, verify=False)
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.InvalidSchema,
                requests.exceptions.MissingSchema,
                requests.exceptions.InvalidURL) as e:

            raise FavIconException(e)

        try:
            h.raise_for_status()
        except HTTPError as e:
            raise FavIconException(f'HTTP Error on favicon url: {favicon_url}')

        if len(h.content) == 0:
            raise FavIconException(f'download_remove_favicon: Zero Length favicon: {favicon_url}')

        # is the returning file SVG? If so, we have to convert it to bitmap (png)
        # content = cairosvg.svg2png(bytestring=h.content) if 'SVG' in from_buffer(h.content) else h.content

        if 'SVG' in from_buffer(h.content) or favicon_url.endswith('.svg'):
            image = cairosvg.svg2png(bytestring=h.content)
        else:
            image = h.content

        if not self.is_bytes_valid_favicon(image):
            raise FavIconException(f'download_remove_favicon: Downloaded icon was not valid image: {favicon_url}')

        return image

    def log_error(self, message):
        log.debug(message)
        self.errors.append(message)

    def fetch_html(self) -> str:
        try:
            # set the user agent to fool economist.com and other sites who care...
            r = requests.get(self.url, timeout=self.TIMEOUT, headers=self.HEADERS, verify=False)

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            raise FavIconException(e)

        # if we were redirected off the domain, then we catch it here
        new_domain_parts = urlparse(r.url)
        new_domain = new_domain_parts.netloc.split(':')[0].lower()

        # now we just re-check favicons on the new domain
        if self.domain != new_domain:
            log.debug(f'Switching domains. {self.domain} -> {new_domain}')
            self.url = r.url
            self._process_meta()

        return r.text

    def find_in_html(self, html:str) -> str:
        """
        Look for a favicon (or apple touch icon) in an html string.

        :param html: The HTML string (often entire page source)
        :param base_url: Base URL for the page (eg http://example.com)
        :return: a string URL of the favicon location or data-uri
        """
        soup = BeautifulSoup(html, 'html5lib')

        # find the first available link to an icon we can download
        target = soup.find('link', attrs={'rel': lambda x: x.lower() in self.HTML_ATTRIBUTES})

        if not target:
            raise FavIconException('Could not find suitable link for favicon extraction')

        href = target.get('href', '')

        return self.calc_href(href)

    def calc_href(self, href: str) -> str:
        """
        Calculate the complete URL based on the base_url and the href fragment

        :param href:
        :param base_url:
        :return:
        """

        if len(href) == 0:
            raise FavIconException(f'Found Favicon HREF was length 0: {href}')

        # for those clever devs who pack the favicon as a data uri
        if href.startswith('data:image'):
            return href

        if href.startswith('http'):
            return href

        if href.startswith('//'):
            return 'http:' + href

        return urljoin(self.base_url, href)

    def is_bytes_valid_favicon(self, data) -> bool:
        """

        :param data:
        :return:
        """
        bytes = BytesIO(data)
        the_magic = from_buffer(bytes.read())

        if any([m in the_magic for m in ['icon', 'PNG', 'GIF', 'JPEG', 'SVG', 'PC bitmap']]):
            return True

        # TODO: detect if all pixels are white or transparent
        # http://stackoverflow.com/a/1963146/1646663
        # http://stackoverflow.com/a/14041871/1646663

        return False

    def get_favicon(self) -> BytesIO:
        """
        Return bytes

        :return:
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
            favicon_url = f"{self.base_url}/favicon.ico"

        try:
            raw_image = self.download_remote_favicon(favicon_url)
            image = resize_image(raw_image)

        except FavIconException as e:
            self.log_error(e)
            image = make_image(self.domain)

        with open(self.filename, 'wb') as f:
            f.write(image)

        # wrap data in BytesIO and send it out
        return BytesIO(image)

def common_locations(domain: str) -> List[str]:
    """
    Produce an array of the most common locations where we might find a favicon

    :param domain: just the base domain name (example.com)
    :return: a list of urls
    """

    # extensions = ['ico','png','gif','jpg','jpeg']
    extensions = ['ico', 'png']
    schemes = ['http', 'https']
    subdomains = ['']

    locations = []

    # check in 20 possible places
    # this is probably a bit excessive
    for ext in extensions:
        for scheme in schemes:
            for subdomain in subdomains:
                url = f'{scheme}://{subdomain}{domain}/favicon.{ext}'
                locations.append(url)

    return locations


def make_image(domain:str) -> bytes:
    """
    Given a domain name, generate a favicon that is just the first letter.

    :param domain:
    :return:
    """
    letter = domain[0].upper()

    b = os.path.dirname(os.path.realpath(__file__))
    font = ImageFont.truetype(f"{b}/assets/fonts/DejaVuSansMono-webfont.ttf", 24)
    img = Image.new("RGBA", (32,32),(128,128,128))
    draw = ImageDraw.Draw(img)
    color = (255,255,255)
    draw.text((8, 1), letter, color,font=font)

    out = BytesIO()

    img.save(out, 'png')
    return out.getvalue()


def resize_image(image:bytes, width:int = 16, height:int = 16) -> bytes:

    img = Image.open(BytesIO(image))
    img = img.convert('RGB') if img.mode == 'CMYK' else img

    img.thumbnail((width, height), Image.ANTIALIAS)

    out = BytesIO()
    img.save(out, 'png')
    val = out.getvalue()
    return val
