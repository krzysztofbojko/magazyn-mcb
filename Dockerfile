# Używamy lekkiego obrazu Pythona
FROM python:3.9-slim

# Install tzdata for timezone support
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy plik zależności i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu aplikacji
COPY . .

# Create a non-root user
RUN useradd -m appuser

# Create instance directory and set permissions
RUN mkdir -p instance && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Eksponujemy port 5000
EXPOSE 5000

# Zmienna środowiskowa dla Flaska
ENV FLASK_APP=app.py

# Komenda startowa:
# 1. Uruchom inicjalizację bazy danych (tworzenie tabel, userów)
# 2. Uruchom serwer produkcyjny Gunicorn na porcie 5000
CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && gunicorn -w 4 -b 0.0.0.0:5000 app:app"]
