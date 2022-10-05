"""This file is used by gunicorn to kick things off."""
from app import app

if __name__ == '__main__':
    app.run()
