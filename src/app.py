from datetime import datetime, timedelta
from typing import Optional
from flask import Flask, send_file, request, make_response
from favicon_extractor import FavIcon, FavIconException
import os
import sys
import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv('env'))

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()]
)

fmt = '%(asctime)s:%(levelname)s:favicon-{}:%(message)s'.format(os.getenv('IMAGE_VERSION'))
logging.basicConfig(format=fmt, stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

@app.route("/")
def grab_favicon():

    url: Optional[str] = request.args.get('url', None)

    try:
        favicon = FavIcon(url, BASE_DIR)

    except FavIconException as e:
        return str(e), 400

    favicon = favicon.get_favicon()

    response = make_response(send_file(favicon, mimetype='image/png', conditional=True))
    response.headers['X-IMAGE-VERSION'] = os.getenv('IMAGE_VERSION')
    response.cache_control.max_age = 315360000 # 1 year

    return response


@app.after_request
def add_header(response):
    then = datetime.now() + timedelta(days=365)
    response.headers['Expires'] = then.strftime("%a, %d %b %Y %H:%M:%S GMT")

    return response
