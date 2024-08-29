FROM python:3.11-slim

WORKDIR /app

COPY ./Worker/ /app
COPY ./commonRessources ./fetchScripts/commonRessources

RUN pip install -r fetchScripts/requirements.txt

CMD tail -f /dev/null

