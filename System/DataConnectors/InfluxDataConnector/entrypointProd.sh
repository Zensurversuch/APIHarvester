#!/bin/bash

python /app/initInflux.py

exec gunicorn --bind 0.0.0.0:5000 app:app
