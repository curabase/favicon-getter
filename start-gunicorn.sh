gunicorn --pythonpath=/usr/src/app/src wsgi:app -b 0.0.0.0:5000 -w $((10 * $(getconf _NPROCESSORS_ONLN) + 1)) --access-logfile - --error-logfile - 
