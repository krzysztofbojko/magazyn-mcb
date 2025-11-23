# ProstyProgramMagazynowy (WMS)

Prosty i intuicyjny system do zarządzania stanami magazynowymi, stworzony z myślą o warsztatach i małych firmach. Aplikacja umożliwia śledzenie stanów, rejestrowanie przyjęć i wydań oraz zarządzanie użytkownikami.

## 🚀 Szybki Start (Docker)

To zalecany sposób uruchomienia. Wymaga zainstalowanego **Docker** oraz **Docker Compose v2**.

1. **Pobierz kod:**
   ```bash
   git clone https://github.com/krzysztofbojko/magazyn-mcb.git
   cd magazyn-mcb
   ```

2. **Uruchom aplikację:**
   ```bash
   docker compose up -d --build
   ```

3. **Gotowe!** Aplikacja jest dostępna pod adresem:
   👉 [http://localhost:5000](http://localhost:5000)

## 📦 Instalacja Ręczna (Python)

Jeśli nie używasz Dockera, potrzebujesz **Python 3.9+**.

1. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```
2. Uruchom serwer:
   ```bash
   python app.py
   ```

## 🔑 Domyślne Konta

System generuje automatycznie dwóch użytkowników przy pierwszym uruchomieniu:

| Rola | Login | Hasło | Uprawnienia |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Pełny dostęp + Zarządzanie użytkownikami |
| **Pracownik** | `pracownik` | `user123` | Obsługa magazynu (bez panelu admina) |

## 📖 Instrukcja Obsługi

### 1. Magazyn (Dashboard)
Główny widok przedstawia listę wszystkich produktów.
- **Dodawanie**: Kliknij `+ Dodaj Produkt`. Nazwy są automatycznie formatowane na WIELKIE LITERY.
- **Wyszukiwanie**: Użyj pola nad tabelą, aby błyskawicznie filtrować listę.
- **Jednostki**: Możesz definiować własne jednostki miary (szt, kg, m, itp.).
- **Usuwanie**: Możesz usunąć produkt, ale **historia jego transakcji pozostanie w systemie**.

### 2. Operacje (Przyjęcia i Wydania)
Aby zmienić stan magazynowy, kliknij przycisk `Operacje` przy wybranym produkcie.
- **Pobierz**: Zmniejsza stan (wydanie towaru). System nie pozwoli wydać więcej niż jest na stanie.
- **Przyjmij**: Zwiększa stan (dostawa towaru).

### 3. Historia
Pełny, niezmienialny rejestr zdarzeń. Każda operacja zapisuje:
- Datę i czas.
- Użytkownika wykonującego akcję.
- Nazwę produktu (zachowaną nawet po jego usunięciu).
- Ilość i typ operacji (Dostawa/Wydanie).

### 4. Panel Administratora
Dostępny tylko dla konta `admin` w zakładce **Użytkownicy**.
- Dodawanie nowych pracowników.
- Resetowanie haseł użytkownikom.
