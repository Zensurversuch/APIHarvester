# Verwende das Python 3.8 Basisimage
FROM python:3.8

# Setze das Arbeitsverzeichnis innerhalb des Containers
WORKDIR /app

# Installiere die Python-Abhängigkeiten aus der requirements.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Kopiere die restlichen Anwendungsdateien
COPY . .

# CMD wird verwendet, um den Standardbefehl für den Container anzugeben, der die Flask-Anwendung startet
CMD ["python", "app.py"]
# Verwende das Python 3.8 Basisimage
FROM python:3.8

# Setze das Arbeitsverzeichnis innerhalb des Containers
WORKDIR /app

# Installiere die Python-Abhängigkeiten aus der requirements.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Kopiere die restlichen Anwendungsdateien
COPY . .

# CMD wird verwendet, um den Standardbefehl für den Container anzugeben, der die Flask-Anwendung startet
CMD ["python", "app.py"]
