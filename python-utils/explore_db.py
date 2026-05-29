import sqlite3

conn = sqlite3.connect("database/Road_Accidents.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)
for t in tables:
    cursor.execute(f"PRAGMA table_info({t[0]})")
    cols = cursor.fetchall()
    print(f"\n{t[0]} columns:", [(c[1], c[2]) for c in cols])
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    print(f"{t[0]} rows:", cursor.fetchone()[0])
conn.close()
