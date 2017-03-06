FROM python:3-onbuild

# Pass the command line arg into the ENV arg, persisting it in the docker image
ARG IMAGE_VERSION
ENV IMAGE_VERSION=$IMAGE_VERSION

EXPOSE 5000

CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:5000", "-w","10", "--access-logfile", "-"]
