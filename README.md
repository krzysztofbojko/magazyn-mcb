# System Magazynowy (WMS) - Instrukcja

Prosty, webowy system do zarządzania stanami magazynowymi, dedykowany dla warsztatów i małych hal produkcyjnych.

## 📋 Wymagania
*   Komputer z systemem Windows, Linux lub macOS.
*   Zainstalowany **Python 3.8** lub nowszy.
*   Przeglądarka internetowa (Chrome, Firefox, Edge).

## 🚀 Instalacja

1.  **Pobierz kod źródłowy** do wybranego katalogu (np. `C:\Magazyn`).
2.  **Otwórz terminal** (Wiersz poleceń / PowerShell) w tym katalogu.
3.  **Zainstaluj wymagane biblioteki** komendą:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Uruchomienie (Standardowe)

1.  W terminalu (będąc w katalogu projektu) uruchom komendę:
    ```bash
    python app.py
    ```
2.  Jeśli zobaczysz komunikat `Running on http://127.0.0.1:5000`, oznacza to, że serwer działa.
3.  Otwórz przeglądarkę i wejdź na adres: [http://127.0.0.1:5000](http://127.0.0.1:5000)

> **Uwaga:** Aby zamknąć serwer, w terminalu naciśnij `CTRL + C`.

## 🐳 Uruchomienie z Dockerem

Jeśli wolisz używać kontenerów, przygotowaliśmy konfigurację Docker.

1.  Upewnij się, że masz zainstalowany **Docker** oraz **Docker Compose**.
2.  W katalogu projektu uruchom:
    ```bash
    docker-compose up -d --build
    ```
3.  Aplikacja zostanie zbudowana i uruchomiona w tle. Dostępna będzie pod adresem: [http://localhost:5000](http://localhost:5000)
4.  **Dane są bezpieczne**: Baza danych jest zapisywana w lokalnym katalogu `instance/`, który jest zamontowany do kontenera.

Aby zatrzymać kontenery (i usunąć je):
```bash
docker-compose down
```

Aby wznowić działanie (lub uruchomić ponownie):
```bash
docker-compose up -d
```

### ⚙️ Konfiguracja Portu (Docker)
Domyślnie aplikacja działa na porcie `5000`. Aby to zmienić (np. na port `80`), edytuj plik `docker-compose.yml`:

```yaml
ports:
  - "80:5000"  # Zmień pierwszą liczbę na wybrany port
```
Po zmianie uruchom ponownie: `docker-compose up -d`

## 🔑 Domyślne Dane Logowania

System automatycznie tworzy dwóch użytkowników przy pierwszym uruchomieniu:

| Rola | Login | Hasło | Opis |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Pełny dostęp + Zarządzanie użytkownikami |
| **Pracownik** | `pracownik` | `user123` | Zarządzanie magazynem (bez panelu użytkowników) |

## 📖 Instrukcja Obsługi

### 1. Panel Główny (Stan Magazynu)
To główne miejsce pracy. Widoczne są tutaj wszystkie produkty.

*   **Wyszukiwanie**: Wpisz nazwę produktu w polu nad tabelą, aby filtrować listę na żywo.
*   **Dodawanie Produktu**: Kliknij zielony przycisk `+ Dodaj Produkt`.
    *   Nazwy produktów są automatycznie zamieniane na **WIELKIE LITERY** (np. "śruby" -> "ŚRUBY").
    *   Możesz zdefiniować "Poziom minimalny" - gdy stan spadnie poniżej tej wartości, w tabeli pojawi się ostrzeżenie "Niski stan".
*   **Jednostki**: Kliknij `Jednostki`, aby dodać nowe miary (np. kpl, m2, szt).
*   **Usuwanie**: Kliknij czerwony przycisk `Usuń` przy produkcie, aby trwale usunąć go z bazy (wymaga potwierdzenia). **Uwaga:** Usuwa to również historię operacji tego produktu!

### 2. Operacje Magazynowe (Pobierz / Przyjmij)
Aby zmienić stan magazynowy, kliknij niebieski przycisk `Operacje` przy danym produkcie.

*   **Pobierz (Wydanie)**: Zmniejsza stan magazynowy. Użyj tego, gdy zabierasz towar z magazynu. System nie pozwoli pobrać więcej niż jest na stanie.
*   **Przyjmij (Dostawa)**: Zwiększa stan magazynowy. Użyj tego, gdy przychodzi nowa dostawa.

### 3. Historia
Zakładka `Historia` w menu górnym pokazuje rejestr wszystkich działań.
*   Możesz sprawdzić **kto**, **co**, **ile** i **kiedy** pobrał lub przyjął.
*   Wydania są oznaczone na czerwono, dostawy na zielono.

### 4. Zarządzanie Użytkownikami (Tylko Admin)
Zakładka `Użytkownicy` jest widoczna tylko dla Administratora.
*   **Dodawanie użytkownika**: Możesz stworzyć nowe konto dla pracownika lub innego administratora.
*   **Zmiana hasła**: Jeśli pracownik zapomni hasła, tutaj możesz ustawić mu nowe.

## 🛠️ Rozwiązywanie Problemów

**Problem: Błąd "no such column" lub błąd bazy danych po aktualizacji.**
*   **Rozwiązanie**:
    1. Zatrzymaj serwer (`CTRL + C`).
    2. Wejdź do katalogu `instance` w folderze projektu.
    3. Usuń plik `magazyn.db`.
    4. Uruchom serwer ponownie (`python app.py`). Baza zostanie utworzona na nowo (dane zostaną wyczyszczone!).

**Problem: Nie mogę się zalogować.**
*   **Rozwiązanie**: Upewnij się, że używasz poprawnych wielkości liter. Jeśli zapomniałeś hasła admina, usuń plik bazy danych (jak wyżej) - hasło zresetuje się do `admin123`.
