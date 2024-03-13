import sqlite3

conn = sqlite3.connect('site.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

username = 'utilisateur'
password = 'motdepasse'
cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))

conn.commit()
conn.close()
