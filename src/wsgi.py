import os
import sys
from app import app
from raven.contrib.flask import Sentry
import logging

sentry = Sentry(app)

if __name__ == '__main__':
    format = '%(asctime)s:%(levelname)s:favicon-{}:%(message)s'\
             .format(os.getenv('IMAGE_VERSION'))
    logging.basicConfig(format=format, stream=sys.stdout, level=logging.DEBUG)

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
