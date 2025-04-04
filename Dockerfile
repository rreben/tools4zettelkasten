# Verwende ein Python-Basis-Image
FROM python:3.9-slim

# Setze Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Projektdateien in den Container
COPY . /app

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Installiere Entwicklungsabhängigkeiten (optional, falls benötigt)
RUN pip install --no-cache-dir -r dev_requirements.txt

# Setze Umgebungsvariablen für den Zettelkasten
ENV ZETTELKASTEN=/app/zettelkasten/mycelium
ENV ZETTELKASTEN_INPUT=/app/zettelkasten/input
ENV ZETTELKASTEN_IMAGES=/app/zettelkasten/mycelium/images

# Exponiere den Port für den Flask-Server
EXPOSE 5000

# Standardbefehl zum Starten des Programms
CMD ["python", "-m", "tools4zettelkasten"]