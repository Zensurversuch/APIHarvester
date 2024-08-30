# Basis-Image
FROM ubuntu:latest

# Arbeitsverzeichnis
WORKDIR /app

COPY ./ /app/
# Aktualisiere Paketlisten und installiere benötigte Pakete
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        python3 \
        python3-pip \
        curl \
        docker.io

# Installiere docker-compose
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Setze den CMD-Befehl, um den Container laufen zu lassen
CMD ["tail", "-f", "/dev/null"]
