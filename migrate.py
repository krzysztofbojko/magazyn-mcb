import sqlite3
import os

DB_FILE = os.path.join('instance', 'magazyn.db')

def get_db_version(cursor):
    try:
        cursor.execute("SELECT version FROM db_version")
        return cursor.fetchone()[0]
    except sqlite3.OperationalError:
        return 0

def set_db_version(cursor, version):
    cursor.execute("DELETE FROM db_version")
    cursor.execute("INSERT INTO db_version (version) VALUES (?)", (version,))

def migrate():
    if not os.path.exists(DB_FILE):
        print(f"Baza danych {DB_FILE} nie istnieje. Uruchom najpierw aplikację, aby utworzyć bazę.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    current_version = get_db_version(cursor)
    print(f"Obecna wersja bazy danych: {current_version}")

    if current_version < 1:
        print("Inicjalizacja tabeli wersji (Wersja 1)...")
        cursor.execute("CREATE TABLE IF NOT EXISTS db_version (version INTEGER)")
        set_db_version(cursor, 1)
        current_version = 1
        conn.commit()

    if current_version < 2:
        print("Migracja do wersji 2 (Dodanie kolumny 'type' do transakcji)...")
        
        # 1. Add column
        try:
            cursor.execute("ALTER TABLE 'transaction' ADD COLUMN type VARCHAR(20)")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("Kolumna 'type' już istnieje, pomijam dodawanie.")
            else:
                raise e

        # 2. Backfill data
        print("Uzupełnianie danych historycznych...")
        cursor.execute("SELECT id, change_amount FROM 'transaction' WHERE type IS NULL")
        transactions = cursor.fetchall()
        
        for t_id, amount in transactions:
            new_type = 'restock' if amount > 0 else 'take'
            cursor.execute("UPDATE 'transaction' SET type = ? WHERE id = ?", (new_type, t_id))
            
        set_db_version(cursor, 2)
        conn.commit()
        print("Migracja do wersji 2 zakończona pomyślnie.")

    else:
        print("Baza danych jest aktualna.")

    conn.close()

if __name__ == "__main__":
    migrate()
