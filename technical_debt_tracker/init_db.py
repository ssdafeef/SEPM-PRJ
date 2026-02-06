import sqlite3

conn = sqlite3.connect('database.db')
conn.execute('''
CREATE TABLE technical_debt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    severity TEXT,
    status TEXT,
    deadline DATE
)
''')
conn.commit()
conn.close()

print("Database created successfully")
