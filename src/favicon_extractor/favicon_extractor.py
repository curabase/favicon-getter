import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datauri import DataURI
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

import magic
import os
import uuid
import logging

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
TIMEOUT = 2


def common_locations(domain):
    """
    Produce an array of the most common locations where we might find a favicon
    :param domain:
    :return: an array of urls
    """
    # extensions = ['ico','png','gif','jpg','jpeg']
    extensions = ['ico', 'png']
    schemes = ['http', 'https']
    subdomains = ['www.', '']

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


def download_or_create_favicon(favicon, domain):
    file_path = os.path.dirname(os.path.realpath(__file__))
    generic_favicon = "{}/generic_favicon.png".format(file_path)

    if favicon.startswith('data:image'):
        log.debug('Found data:image uri!')
        uri = DataURI(favicon)
        data = uri.data
        return Image.open(BytesIO(data)).resize((32, 32))

    if favicon == 'missing':
        log.debug('{}:favicon missing. Generating one'.format(domain))
        return Image.open(generic_favicon).resize((32, 32))
        # return make_image(domain)

    r = requests.get(favicon, timeout=TIMEOUT, headers=HEADERS)

    # response and that the file exists and is not empty
    if (r.status_code == requests.codes.ok) and (len(r.text) > 0):
        return Image.open(BytesIO(r.content)).resize((32, 32))
    else:
        return Image.open(generic_favicon).resize((32, 32))
        # return make_image(domain)


def get_favicon(domain, html=None):

    # TODO: check DNS / check DNS on www.

    base_url = 'http://{}'.format(domain)

    if html is None:
        try:

            # set the user agent to fool economist.com and other sites
            # who care...
            r = requests.get(base_url, timeout=TIMEOUT, headers=HEADERS)
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
            return 'missing'

    favicon = find_in_html(html, base_url)
    if favicon == 'missing':
        for url in common_locations(domain):
            log.debug('trying {}'.format(url))
            if poke_url(url):
                return url

    return favicon


def find_in_html(html, base_url):
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
        # this line -- it filters out all .svg hrefs and returns the
        # first sane one
        icons = soup.find_all("link", attrs={'rel': lambda x: x and x.lower()=='icon'})
        href = [l.get('href') for l in icons if not l.get('href').lower().endswith('.svg')][0]
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


def poke_url(url, recursions=0):
    """

    :param url:
    :param recursions:
    :return:
    """
    # we assume the worst (missing) unless changed below
    result = False

    try:
        # need to set headers here to fool sites like cafepress.com...
        h = requests.get(url,
                         allow_redirects=False,
                         timeout=TIMEOUT,
                         headers=HEADERS)
    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError) as e:
        return result

    if h.status_code == 200:
        fname = '/tmp/{}'.format(str(uuid.uuid4()))
        f = open(fname, 'wb')
        f.write(h.content)
        f.close()

        the_magic = magic.from_file(fname)

        if any([m in the_magic for m in [b'icon', b'PNG', b'GIF', b'JPEG']]):
            result = h.url

        # TODO: detect if all pixels are white or transparent
        # http://stackoverflow.com/a/1963146/1646663
        # http://stackoverflow.com/a/14041871/1646663

        os.remove(fname)

    return result


def make_image(domain):
    img = Image.new('RGB', (32, 32), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(
               os.path.dirname(os.path.realpath(__file__)) +
               "/Andale Mono.ttf", 24)
    color = (0, 0, 0)
    draw.text((0, 0), domain[0].upper(), color, font=font)

    return img


def calc_href(href, base_url):
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
