FROM python:3

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN pip install raven[flask]


RUN mkdir -p /usr/src/app
COPY src/ /usr/src/app

# Pass the command line arg into the ENV arg, persisting it in the docker image
ARG IMAGE_VERSION
ENV IMAGE_VERSION=$IMAGE_VERSION

EXPOSE 5000

COPY start-gunicorn.sh /usr/src/app/start-gunicorn.sh
RUN chmod +x /usr/src/app/start-gunicorn.sh

RUN mkdir /icons && chmod 777 /icons

#CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:5000", "-w","10", "--access-logfile", "-"]

CMD "/usr/src/app/start-gunicorn.sh"
