import sqlite3
import os
from secret import notes_path
from note import read_notes
from datetime import datetime

DATABASE = 'notes.db'
SCHEMA = 'schema.sql'

def init_notes_db(cursor, notes):
    for note in notes:
        cursor.execute(
            "INSERT INTO notes(name, content, title, created) VALUES (?, ?, ?, ?)", 
            (note.name, note.content, note.title, note.datetime))

def init_dates_db(cursor, dates):
    for date in dates:
        cursor.execute("INSERT INTO dates(date) VALUES (?)", (date,))

def init_dates_notes_db(cursor, notes):
    #TODO Find note_id, date_id. Maybe create NoteCollection that has assigns the id.
    for note in notes:
        for date in note.dates:
            cursor.execute("INSERT INTO notes_dates(note_id, date_id) VALUES (?,?)", (note, date))

def init_notes_links_db(cursor, notes):
    #TODO Find note_id. Add note links.
    for from_note in notes:
        for to_note in from_note.links:
            cursor.execute("INSERT INTO notes_links(from_note_id, to_note_id) VALUES (?,?)", (from_note, to_note))

def make_dates_list(start: str, end: str):
    start_date = datetime.datetime.strptime(start, "%d-%m-%Y")
    end_date = datetime.datetime.strptime(end, "%d-%m-%Y")
    return [start_date + datetime.timedelta(days=x) for x in range(0, (end_date-start_date).days)]

if __name__ == "__main__": 
    notes = read_notes(notes_path)
    dates = sorted(list(set([d for note in notes for d in note.dates])))

    db_connection = sqlite3.connect(DATABASE)
    with open(SCHEMA) as f:
        db_connection.executescript(f.read())
    cursor = db_connection.cursor()
    init_notes_db(cursor, notes)
    init_dates_db(cursor, dates)
    db_connection.commit() # If you don’t call this method, anything you did since the last call to commit() is not visible from other database connections. https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection
    db_connection.close()
    

