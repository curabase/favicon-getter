import os
from datetime import datetime, timedelta
from typing import Optional

import sentry_sdk
from dotenv import find_dotenv, load_dotenv
from flask import Flask, make_response, request, send_file
from sentry_sdk.integrations.flask import FlaskIntegration

from favicon_extractor import FavIcon, FavIconException

load_dotenv(find_dotenv('env'))

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ONE_YEAR = 365


@app.route('/')
def grab_favicon():
    """
    Get a favicon from a url/domain.

    :return: HTTP Response
    """
    url: Optional[str] = request.args.get('url', None)

    try:
        favicon = FavIcon(url, BASE_DIR)

    except FavIconException as exception:
        return str(exception), 400

    favicon = favicon.get_favicon()

    response = make_response(
        send_file(
            favicon,
            mimetype='image/png',
            conditional=True,
        ),
    )
    response.headers['X-IMAGE-VERSION'] = os.getenv('IMAGE_VERSION')
    response.cache_control.max_age = 315360000  # 1 year

    return response


@app.after_request
def add_header(response):
    """Add headers to all responses."""
    then = datetime.now() + timedelta(days=ONE_YEAR)
    response.headers['Expires'] = then.strftime('%a, %d %b %Y %H:%M:%S GMT')

    return response
