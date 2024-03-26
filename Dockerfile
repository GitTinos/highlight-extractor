FROM python:3.11-slim

# Imposta una directory di lavoro
WORKDIR /app

# Imposta variabili d'ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installa dipendenze di sistema
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libpq-dev make \
  # Aggiungi Poppler e dipendenze per pdf2image e OpenCV
  && apt-get install -y poppler-utils \
  && apt-get install -y tesseract-ocr \
  && apt-get install -y tesseract-ocr-ita \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Installa le dipendenze Python
COPY src/requirements.txt /app/
RUN pip install --upgrade pip \
  && pip install -r requirements.txt

# Copia il progetto Fastapi
COPY ./src /app/