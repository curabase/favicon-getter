from urllib.parse import urlparse

from PIL import ImageFont, Image, ImageDraw
import os
import socket
import logging
import sys


fmt = '%(asctime)s:%(levelname)s:favicon-{}:%(message)s'.format(os.getenv('IMAGE_VERSION'))
logging.basicConfig(format=fmt, stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
MEDIA_ROOT = f'{BASE_DIR}/../icons'


def generate_favicon(domain:str) -> str:
    """
    Given a domain name, generate a favicon that is just the first letter.

    :param domain:
    :return:
    """
    letter = domain[0].upper()
    filename = f"{MEDIA_ROOT}/{letter}.png"

    if not os.path.isfile(filename):

        font = ImageFont.truetype(f"{BASE_DIR}/../fonts/DejaVuSansMono-webfont.ttf", 24)
        img=Image.new("RGBA", (32,32),(128,128,128))
        draw = ImageDraw.Draw(img)
        draw.text((8, 1), letter,(255,255,255),font=font)

        img.save(filename)

    return filename


def check_dns(domain:str) -> bool:
    """
    Check that the domain/hostname given actually resolves.
    """
    log.debug("Checking DNS...")

    try:
        socket.getaddrinfo(domain, None)
    except socket.error:
        log.debug('DNS LOOKUP FAILED: generating favicon')
        return False
    else:
        return True


def check_url(url:str) -> bool:
    """
    Given a URL validate its format


    https://stackoverflow.com/a/45050545/1646663

    :param url:
    :return:
    """
    min_attr = ('scheme', 'netloc')
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return True
        else:
            return False
    except:
        return False