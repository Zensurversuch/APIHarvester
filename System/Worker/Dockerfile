FROM python:3.11-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    sudo

# Install Docker in order to be able to get the real name of the container afterwards
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && echo "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli

WORKDIR /app

COPY ./Worker/ /app
COPY ./commonRessources ./fetchScripts/commonRessources
COPY ./commonRessources ./heartbeat/commonRessources

RUN pip install -r requirements.txt

CMD ["python", "heartbeat/heartbeats.py"]

