gunicorn -k flask_sockets.worker -b 0.0.0.0:5000 --workers 4 --threads 1 app.application
