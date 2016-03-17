import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

import magic
import os
import uuid

# TODO: convert this into a class
# TODO: Need to handle favicons that use data: urls like this guy: http://ajf.me/

def download_or_create_favicon(favicon, domain):
    if favicon == 'missing':
        return make_image(domain)

    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"
    headers = {'User-agent': user_agent}
    r = requests.get(favicon, timeout=3, headers=headers)

    # response and that the file exists and is not empty
    if (r.status_code == requests.codes.ok) and (len(r.text) > 0):
        return Image.open(BytesIO(r.content)).resize((32, 32))
    else:
        return make_image(domain)


def get_favicon(domain, html=None):

    base_url = 'http://{}'.format(domain)

    extensions = ['ico','png','gif','jpg','jpeg']
    schemes    = ['http', 'https']
    subdomains = ['www.','']
    
    common_locations = []

    # check in 20 possible places 
    for ext in extensions:
        for scheme in schemes:
            for subdomain in subdomains:
                url = '{}://{}{}/favicon.{}'.format(scheme,subdomain,domain,ext)
                common_locations.append(url)
                if poke_url(url):
                    return url


    if html is None:
        try:

            # set the user agent to fool economist.com and other sites who care...
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"
            headers = {'User-agent': user_agent}
            r = requests.get(base_url, timeout=3, headers=headers)
            html = r.text

            # if we were redirected off the domain, then we catch it here
            new_domain_parts = urlparse(r.url)
            new_domain = new_domain_parts.netloc.lstrip('www.')

            # now we just re-check favicons on the new domain
            if domain != new_domain:
                for o in common_locations:
                    url = o.replace(domain,new_domain)
                    if poke_url(url):
                        return url

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            pass

    favicon = find_in_html(html,base_url)

    return favicon


def find_in_html(html, base_url):

    favicon = 'missing'
    soup = BeautifulSoup(html, 'html5lib')

    if soup.find("link", rel="shortcut"):
        href = soup.find("link", rel="shortcut")['href']
        if len(href) > 0:
            favicon = calc_href(href, base_url)

    elif soup.find("link", rel="icon"):
        # this fuckin' line -- it filters out all .svg hrefs and returns the first sane one
        href = [l.get('href') for l in soup.find_all("link", rel="icon") if not l.get('href').lower().endswith('.svg')][0]
        if len(href) > 0:
            favicon = calc_href(href, base_url)

    elif soup.find("link", rel="apple-touch-icon"):
        href = soup.find("link", rel="apple-touch-icon")['href']
        if len(href) > 0:
            favicon = calc_href(href, base_url)

    elif soup.find("link", rel="apple-touch-icon-precomposed"):
        href = soup.find("link", rel="apple-touch-icon-precomposed")['href']
        if len(href) > 0:
            favicon = calc_href(href, base_url)

    return favicon


def poke_url(url, recursions=0):

    # we assume the worst (missing) unless changed below
    result = False

    try:
        # need to set headers here to fool sites like cafepress.com...
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"
        headers = {'User-agent': user_agent}
        h = requests.get(url, allow_redirects=False, timeout=3, headers=headers)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        return result

    if h.status_code == 200:
        fname = '/tmp/{}'.format(str(uuid.uuid4()))
        f = open(fname, 'wb')
        f.write(h.content)
        f.close()

        the_magic = magic.from_file(fname)
        if b"icon" in the_magic:
            result = h.url

        if b"PNG" in the_magic:
            # TODO: detect if all pixels are white or transparent
            # http://stackoverflow.com/a/1963146/1646663
            # http://stackoverflow.com/a/14041871/1646663
            result = h.url

        if b"GIF" in the_magic:
            # TODO: detect if all pixels are white or transparent
            # http://stackoverflow.com/a/1963146/1646663
            # http://stackoverflow.com/a/14041871/1646663
            result = h.url

        os.remove(fname)

    return result


def make_image(domain):
    img = Image.new('RGB', (32, 32), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.dirname(os.path.realpath(__file__)) + "/Andale Mono.ttf", 24)
    color = (0, 0, 0)
    draw.text((0, 0), domain[0].upper(), color, font=font)

    return img


def calc_href(href, base_url):

    if href.startswith('http'):
        return href

    if href.startswith('//'):
        return 'http:' + href

    return urljoin(base_url, href)


if __name__ == '__main__':
    import sys

    domain = sys.argv[1]
    print(get_favicon(domain))
