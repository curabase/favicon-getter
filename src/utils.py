"""Various utilities for validating input and generating placeholders."""
import logging
import os
import socket
import sys
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont

fmt = '%(asctime)s:%(levelname)s:favicon-{}:%(message)s'.format(os.getenv('IMAGE_VERSION'))
logging.basicConfig(format=fmt, stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
MEDIA_ROOT = '{0}/../icons'.format(BASE_DIR)


def generate_favicon(domain: str) -> str:
    """
    Given a domain name, generate a favicon that is just the first letter.

    :param domain:
    :return:
    """
    letter = domain[0].upper()
    filename = '{0}/{1}.png'.format(MEDIA_ROOT, letter)

    if not os.path.isfile(filename):

        font = ImageFont.truetype(
            '{0}/../fonts/DejaVuSansMono-webfont.ttf'.format(BASE_DIR),
            24,
        )
        img = Image.new('RGBA', (32, 32), (128, 128, 128))
        draw = ImageDraw.Draw(img)
        draw.text((8, 1), letter, (255, 255, 255), font=font)

        img.save(filename)

    return filename


def check_dns(domain: str) -> bool:
    """Check that the domain/hostname given actually resolves."""
    log.debug('Checking DNS...')

    try:
        socket.getaddrinfo(domain, None)
    except socket.error:
        log.debug('DNS LOOKUP FAILED: generating favicon')
        return False

    return True


def check_url(url: str) -> bool:
    """
    Given a URL validate its format.

    https://stackoverflow.com/a/45050545/1646663

    :param url:
    :return:
    """
    min_attr = ('scheme', 'netloc')
    try:
        url_parts = urlparse(url)
    except Exception:
        return False

    return all([url_parts.scheme, url_parts.netloc])
