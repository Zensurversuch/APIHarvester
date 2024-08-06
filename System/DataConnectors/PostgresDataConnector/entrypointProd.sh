#!/bin/bash

python /app/initPostgres.py

exec gunicorn --bind 0.0.0.0:5000 app:app
