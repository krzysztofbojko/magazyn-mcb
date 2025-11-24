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

    if current_version < 3:
        print("Migracja do wersji 3 (Właściciele i Float)...")
        
        # 1. Create product_owners table
        print("Tworzenie tabeli product_owners...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_owners (
                product_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (product_id, user_id),
                FOREIGN KEY(product_id) REFERENCES product (id),
                FOREIGN KEY(user_id) REFERENCES user (id)
            )
        """)

        # 2. Recreate Product table
        print("Aktualizacja tabeli product...")
        try:
            cursor.execute("ALTER TABLE product RENAME TO product_old")
            cursor.execute("""
                CREATE TABLE product (
                    id INTEGER NOT NULL,
                    name VARCHAR(150) NOT NULL,
                    quantity FLOAT,
                    unit_id INTEGER NOT NULL,
                    min_level INTEGER,
                    owners_all BOOLEAN,
                    PRIMARY KEY (id),
                    UNIQUE (name),
                    FOREIGN KEY(unit_id) REFERENCES unit (id)
                )
            """)
            # Copy data
            cursor.execute("""
                INSERT INTO product (id, name, quantity, unit_id, min_level, owners_all)
                SELECT id, name, CAST(quantity AS FLOAT), unit_id, min_level, 0 FROM product_old
            """)
            cursor.execute("DROP TABLE product_old")
        except sqlite3.OperationalError as e:
            print(f"Błąd podczas migracji tabeli product: {e}")
            # Attempt rollback/recovery if needed, but for now just raise
            raise e

        # 3. Recreate Transaction table
        print("Aktualizacja tabeli transaction...")
        try:
            cursor.execute("ALTER TABLE 'transaction' RENAME TO transaction_old")
            cursor.execute("""
                CREATE TABLE 'transaction' (
                    id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER,
                    product_name VARCHAR(150) NOT NULL,
                    change_amount FLOAT NOT NULL,
                    type VARCHAR(20),
                    timestamp DATETIME,
                    PRIMARY KEY (id),
                    FOREIGN KEY(user_id) REFERENCES user (id)
                )
            """)
            # Copy data
            cursor.execute("""
                INSERT INTO 'transaction' (id, user_id, product_id, product_name, change_amount, type, timestamp)
                SELECT t.id, t.user_id, t.product_id, COALESCE(p.name, 'Unknown'), CAST(t.change_amount AS FLOAT), t.type, t.timestamp 
                FROM transaction_old t
                LEFT JOIN product p ON t.product_id = p.id
            """)
            cursor.execute("DROP TABLE transaction_old")
        except sqlite3.OperationalError as e:
             print(f"Błąd podczas migracji tabeli transaction: {e}")
             raise e

        set_db_version(cursor, 3)
        conn.commit()
        print("Migracja do wersji 3 zakończona pomyślnie.")

    else:
        print("Baza danych jest aktualna.")

    conn.close()

if __name__ == "__main__":
    migrate()
