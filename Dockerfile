# Używamy lekkiego obrazu Pythona
FROM python:3.9-slim

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy plik zależności i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu aplikacji
COPY . .

# Tworzymy katalog na bazę danych (jeśli nie istnieje)
RUN mkdir -p instance

# Eksponujemy port 5000
EXPOSE 5000

# Zmienna środowiskowa dla Flaska
ENV FLASK_APP=app.py

# Komenda startowa:
# 1. Uruchom inicjalizację bazy danych (tworzenie tabel, userów)
# 2. Uruchom serwer produkcyjny Gunicorn na porcie 5000
CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && gunicorn -w 4 -b 0.0.0.0:5000 app:app"]
