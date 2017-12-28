from flask import Flask, send_file, request, make_response

from favicon_extractor.favicon_extractor import \
    get_favicon, \
    download_or_create_favicon

import socket
import os
import sys
import logging
from raven.contrib.flask import Sentry

fmt = '%(asctime)s:%(levelname)s:favicon-{}:%(message)s' \
    .format(os.getenv('IMAGE_VERSION'))
logging.basicConfig(format=fmt, stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

app = Flask(__name__)
sentry = Sentry(app)

MEDIA_ROOT = '{}/icons'.format(os.path.dirname(os.path.realpath(__file__)))


@app.route("/")
def grab_favicon():

    domain = request.args.get('domain', None)
    favicon = request.args.get('favicon', None)

    if domain is None:
        return 'No domain given'

    domain = domain.split('?')[0].split('/')[0]

    filename = '{}/{}.png'.format(MEDIA_ROOT, domain)

    # if the file exists, the just return it now
    if os.path.isfile(filename) and favicon is None:
        return do_return_file(filename)

    # resolve DNS on domain
    log.info("Checking DNS...")
    if favicon is None and check_dns(domain) is False:
        log.debug('Domain lookup failed. Trying www..')
        if check_dns('www.{}'.format(domain)):
            log.debug('WWW Strategy succeeded!')
            domain = 'www.{}'.format(domain)
        else:
            log.debug('WWW strategy failed. Fallback to generic icon')
            favicon = 'missing'

    # if favicon location was not set from the url params,
    # then we must hunt for it
    favicon = get_favicon(domain) if favicon is None else favicon

    img = download_or_create_favicon(favicon, domain)
    img.save(filename)

    return do_return_file(filename)


def do_return_file(filename):
    response = make_response(send_file(filename,
                                       mimetype='image/png',
                                       conditional=True
                                       ))
    response.headers['X-IMAGE-VERSION'] = os.getenv('IMAGE_VERSION')
    return response


def check_dns(domain):
    """
    Check that the domain/hostname given actually resolves.
    """
    try:
        socket.getaddrinfo(domain, None)
    except socket.error:
        return False
    else:
        return True


if __name__ == "__main__":

    debug = os.getenv('DEBUG', False)
    if type(debug) == str:
        debug = debug.lower() in ['1', 'yes', 'true']
    app.run(host='0.0.0.0', debug=debug)

