#! /bin/bash
gunicorn -w 10 app:app -b 0.0.0.0:80 --pythonpath=/home/ubuntu/dashboard/utils/ -D

