import sqlite3
import os
print(f'>>> {os.path.abspath("football_matches.db")} <<<')


conn = sqlite3.connect('/Users/jason/PycharmProjects/soccer/templates/football_matches.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ Table 'matches' exists!")
else:
    print("❌ Table 'matches' does NOT exist!")

conn.close()