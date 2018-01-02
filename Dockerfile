FROM python:3

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir -p /app
COPY src /app

# Pass the command line arg into the ENV arg, persisting it in the docker image
ARG IMAGE_VERSION
ENV IMAGE_VERSION=$IMAGE_VERSION

EXPOSE 5000

COPY start-gunicorn.sh /start-gunicorn.sh
RUN chmod +x /start-gunicorn.sh

RUN mkdir /app/icons && chmod 777 /app/icons

#CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:5000", "-w","10", "--access-logfile", "-"]

WORKDIR /app

CMD "/start-gunicorn.sh"
