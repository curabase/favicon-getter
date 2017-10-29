
import os

from app import app
from raven.contrib.flask import Sentry

sentry = Sentry(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
