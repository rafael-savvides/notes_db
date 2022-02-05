import sqlite3

db_connection = sqlite3.connect('notes.db')

with open('schema.sql') as f:
    db_connection.executescript(f.read())

cursor = db_connection.cursor()
cursor.execute("INSERT INTO notes (content) VALUES (?)", ('# The First Note',))
cursor.execute("INSERT INTO notes (content) VALUES (?)", ('_Another note_',))

db_connection.commit()
db_connection.close()
