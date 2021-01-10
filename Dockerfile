FROM python:3.8-slim

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y \
            build-essential \
            python3-dev \
            python3-pip \
            python3-setuptools \
            python3-wheel \
            python3-cffi \
            libcairo2 \
            libpango-1.0-0 \
            libpangocairo-1.0-0 \
            libgdk-pixbuf2.0-0 \
            libffi-dev \
            shared-mime-info

RUN pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN mkdir -p /app
COPY src /app

# Pass the command line arg into the ENV arg, persisting it in the docker image
ARG IMAGE_VERSION
ENV IMAGE_VERSION=$IMAGE_VERSION

EXPOSE 8000

COPY gunicorn_settings.py /gunicorn_settings.py
RUN mkdir /app/icons && chmod 777 /app/icons

WORKDIR /app

CMD ["gunicorn", "-c", "/gunicorn_settings.py", "wsgi:app"]