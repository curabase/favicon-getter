from flask import Flask, send_file, request

from favicon_extractor.favicon_extractor import \
    get_favicon, \
    download_or_create_favicon

import socket
import os

app = Flask(__name__)

MEDIA_ROOT = '/icons'


@app.route("/")
def grab_favicon():

    domain = request.args.get('domain', None)
    favicon = request.args.get('favicon', None)

    if domain is None:
        return 'No domain given'

    domain = domain.split('?')[0].split('/')[0]

    filename = '{}/{}.png'.format(MEDIA_ROOT, domain)

    # if the file exists, the just return it now
    if os.path.isfile(filename):
        return send_file(filename, mimetype='image/png', conditional=True)

    # resolve DNS on domain
    try:
        socket.create_connection((domain, 80), 5)
    except socket.error:
        favicon = 'missing' if favicon is None else favicon

    # if favicon location was not set from the url params,
    # the we must hunt for it
    if favicon is None:
        favicon = get_favicon(domain)

    img = download_or_create_favicon(favicon, domain)
    img.save(filename)

    return send_file(filename, mimetype='image/png', conditional=True)


if __name__ == "__main__":
    debug = os.getenv('DEBUG', False)
    if type(debug) == str:
        debug = debug.lower() in ['1', 'yes', 'true']
    app.run(host='0.0.0.0', debug=debug)
