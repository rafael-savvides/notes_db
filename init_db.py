import sqlite3
import os
from secret import notes_path
from note import Note
from app import DATABASE

SCHEMA = 'schema.sql'

def insert_notes_to_db(cursor, notes_path):
    note_path_list = [p for p in os.listdir(notes_path) if p.endswith('.md')]
    for note_name in note_path_list:
        note_name_abs = os.path.join(notes_path, note_name)
        note = Note(note_name_abs)
        insert_to_db(cursor, note)

def insert_to_db(cursor, note: Note):
    cursor.execute(
        "INSERT INTO notes(basename, content, title) VALUES (?, ?, ?)", 
        (note.basename, note.content, note.title))


if __name__ == "__main__": 
    db_connection = sqlite3.connect(DATABASE)

    with open(SCHEMA) as f:
        db_connection.executescript(f.read())

    cursor = db_connection.cursor()
    insert_notes_to_db(cursor, notes_path)

    db_connection.commit() # If you don’t call this method, anything you did since the last call to commit() is not visible from other database connections. https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection
    db_connection.close()
