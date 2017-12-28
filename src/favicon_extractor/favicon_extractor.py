import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datauri import DataURI
from PIL import Image, ImageDraw, ImageFont
import cairosvg
from io import BytesIO

from magic import from_file, from_buffer
import os
import uuid
import logging

from typing import Union, List

log = logging.getLogger(__name__)

"""
TODO: convert this into a class
TODO: check a random page to force a 404. Then try to pull favicon from here
      heb.com is trying to block bots using JS on their homepage
"""

HEADERS = {
    'User-agent': ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/48.0.2564.103 Safari/537.36")
}
TIMEOUT = 10


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
                url = '{}://{}{}/favicon.{}'.format(
                                                scheme,
                                                subdomain,
                                                domain, ext)
                locations.append(url)

    return locations


def download_or_create_favicon(favicon: str, domain: str) -> Image:
    """

    :param favicon:
    :param domain:
    :return:
    """
    file_path = os.path.dirname(os.path.realpath(__file__))
    generic_favicon = "{}/generic_favicon.png".format(file_path)

    # handle the case for data: URIs
    if favicon.startswith('data:image'):
        uri = DataURI(favicon)
        data = BytesIO(uri.data)

    # Favicon was determined to be missing, so use a generic icon
    elif favicon == 'missing':
        data = generic_favicon

    # Looks like a normal favicon url, lets go get it
    elif favicon.startswith('http'):
        r = download_remote_favicon(favicon)
        data = BytesIO(r) if r else generic_favicon
        # return make_image(domain)

    img = Image.open(data)
    img = img.convert('RGB') if img.mode == 'CMYK' else img

    return img


def get_favicon(domain: str, html: str=None) -> str:
    """
    Find the favicon for a domain or a given HTML string

    :param domain: domain name (eg example.com)
    :param html: an HTML string (default is None)

    :return: string uri location of the favicon (could be http: or data:image)
    """

    # TODO: check DNS / check DNS on www.
    base_url = 'http://{}'.format(domain)

    if html is None:
        try:

            # set the user agent to fool economist.com and other sites
            # who care...
            r = requests.get(base_url, timeout=TIMEOUT, headers=HEADERS, verify=False)
            html = r.text

            # if we were redirected off the domain, then we catch it here
            new_domain_parts = urlparse(r.url)
            new_domain = new_domain_parts.netloc

            # now we just re-check favicons on the new domain
            if domain != new_domain:
                log.debug('Switching domains. {} -> {}'.format(domain, new_domain))
                return get_favicon(new_domain)

        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            if 'www' not in domain:
                return get_favicon('www.{}'.format(domain))
            return 'missing'

    favicon_uri = find_in_html(html, base_url)
    if is_uri_valid_favicon(favicon_uri) is False:
        for url in common_locations(domain):
            log.debug('trying {}'.format(url))
            if is_uri_valid_favicon(url):
                return url

    return favicon_uri


def find_in_html(html: str, base_url: str) -> str:
    """
    Look for a favicon (or apple touch icon) in an html string.

    :param html: The HTML string (often entire page source)
    :param base_url: Base URL for the page (eg http://example.com)
    :return: a string URL of the favicon location or data-uri
    """

    soup = BeautifulSoup(html, 'html5lib')

    # test if favicon is loaded uses data:image uri scheme
    target = soup.find('link', attrs={'rel': lambda x: x and x.lower()=='shortcut'})
    if target:
        href = target.get('href', '')

        if href.startswith('data:image'):
            return href

        if len(href) > 0:
            return calc_href(href, base_url)

    target = soup.find('link', attrs={'rel': lambda x: x and x.lower()=='icon'})
    if target:
        href = target.get('href')
        if len(href) > 0:
            return calc_href(href, base_url)

    target = soup.find('link', attrs={'rel': lambda x: x and x.lower()=='apple-touch-icon'})
    if target:
        href = target.get('href')
        if len(href) > 0:
            return calc_href(href, base_url)

    target = soup.find('link', attrs={'rel': lambda x: x and x.lower()=='apple-touch-icon-precomposed'})
    if target:
        href = target.get('href')
        if len(href) > 0:
            return calc_href(href, base_url)

    return 'missing'


def is_uri_valid_favicon(uri: str) -> bool:
    """

    :param uri:
    :return:
    """

    if uri.startswith('http') is False and uri.startswith('data:image') is False:
        return False

    if uri.startswith('http'):
        data = download_remote_favicon(uri)

    if uri.startswith('data:image'):
        data = DataURI(uri).data

    return is_bytes_valid_favicon(BytesIO(data)) if data else False


def is_bytes_valid_favicon(data: BytesIO) -> bool:
    """

    :param data:
    :return:
    """
    if type(data) is not BytesIO:
        raise TypeError('Data is not type BytesIO')

    result = False

    fname = '/tmp/{}'.format(str(uuid.uuid4()))
    f = open(fname, 'wb')
    f.write(data.read())
    f.close()

    the_magic = from_file(fname)

    if any([m in the_magic for m in ['icon', 'PNG', 'GIF', 'JPEG', 'SVG']]):
        result = True

    # TODO: detect if all pixels are white or transparent
    # http://stackoverflow.com/a/1963146/1646663
    # http://stackoverflow.com/a/14041871/1646663

    os.remove(fname)

    return result


def download_remote_favicon(url: str) -> Union[BytesIO, bool]:
    """

    :param url:
    :return:
    """
    if not url.startswith('http'):
        raise ValueError('Must be a URL that starts with http or https')

    try:
        # need to set headers here to fool sites like cafepress.com...
        h = requests.get(url,
                         allow_redirects=True,
                         timeout=TIMEOUT,
                         headers=HEADERS,
                         verify=False)
    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.InvalidSchema,
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidURL) as e:
        log.debug('download_remote_favicon:{}'.format(e))
        return False

    if h.status_code == 404:
        return False

    # is the returning file SVG? If so, we have to convert it to bitmap (png)
    #content = cairosvg.svg2png(bytestring=h.content) if 'SVG' in from_buffer(h.content) else h.content

    if 'SVG' in from_buffer(h.content) or url.endswith('.svg'):
        content = cairosvg.svg2png(bytestring=h.content)
    else:
        content = h.content

    return content if h.status_code == 200 and (len(content) > 0) else False


def make_image(domain: str) -> Image:
    """

    :param domain:
    :return:
    """

    img = Image.new('RGB', (32, 32), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(
               os.path.dirname(os.path.realpath(__file__)) +
               "/Andale Mono.ttf", 24)
    color = (0, 0, 0)
    draw.text((0, 0), domain[0].upper(), color, font=font)

    return img


def calc_href(href: str, base_url: str) -> str:
    """
    Calculate the complete URL based on the base_url and the href fragment
    :param href:
    :param base_url:
    :return:
    """
    if href.startswith('http'):
        return href

    if href.startswith('//'):
        return 'http:' + href

    return urljoin(base_url, href)


if __name__ == '__main__':
    import sys

    domain = sys.argv[1]
    print(get_favicon(domain))
