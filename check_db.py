import sqlite3

conn = sqlite3.connect("neurotrack_mvp.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("--- Tables in neurotrack_mvp.db ---")
for table in tables:
    print(f"✅ {table[0]}")

conn.close()