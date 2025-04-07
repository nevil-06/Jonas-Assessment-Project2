import sqlite3
import os

DB_PATH = "data/northwind.db"
SCHEMA_PATH = "data/northwind.sql"
INDEX_PATH = "setup/create_indexes.sql"

def db_exists(path):
    """Check if database file exists and is not empty"""
    return os.path.exists(path) and os.path.getsize(path) > 0

def initialize_database():
    """Creates the database, tables, and indexes"""
    if db_exists(DB_PATH):
        print("✅ Database already exists. Skipping initialization.")
        return

    print("🛠️ Setting up database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🔹 Ensure foreign keys are enforced
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1️⃣ Apply schema first
    print("📜 Creating tables...")
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)  # Run schema

    # 🔍 Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("✅ Tables created:", [t[0] for t in tables])

    # 2️⃣ Now, apply indexes
    print("⚡ Creating indexes...")
    with open(INDEX_PATH, "r") as f:
        index_sql = f.read()
        cursor.executescript(index_sql)  # Run indexing script

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()
