import sqlite3
import os
from secret import notes_path
from note import read_notes, NoteCollection
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

def init_notes_dates_db(cursor, notes):
    for note in notes:
        for date in note.dates:
            #TODO Can use executemany() instead of execute + for loop.
            date_id = cursor.execute("select id from dates where date == :d", {'d': date}).fetchall()[0][0]
            cursor.execute("INSERT INTO notes_dates(note_id, date_id) VALUES (?,?)", (note.id, date_id))

def init_notes_links_db(cursor, note_collection):
    for to_note in note_collection.notes:
        for from_note in note_collection.get_backlinks(to_note):
            cursor.execute("INSERT INTO notes_links(from_note_id, to_note_id) VALUES (?,?)", (from_note.id, to_note.id))

def make_dates_list(start: str, end: str):
    start_date = datetime.datetime.strptime(start, "%d-%m-%Y")
    end_date = datetime.datetime.strptime(end, "%d-%m-%Y")
    return [start_date + datetime.timedelta(days=x) for x in range(0, (end_date-start_date).days)]

if __name__ == "__main__": 
    nc = NoteCollection(notes_path)
    dates = sorted(list(set([d for note in nc.notes for d in note.dates])))

    db_connection = sqlite3.connect(DATABASE)
    with open(SCHEMA) as f:
        db_connection.executescript(f.read())
    cursor = db_connection.cursor()
    init_notes_db(cursor, nc.notes)
    init_dates_db(cursor, dates)
    db_connection.commit() # If you don’t call this method, anything you did since the last call to commit() is not visible from other database connections. https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection
    init_notes_dates_db(cursor, nc.notes)
    db_connection.commit()
    init_notes_links_db(cursor, nc)
    db_connection.commit()
    db_connection.close()
    

