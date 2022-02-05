import sqlite3
import markdown
from flask import Flask, render_template, request, flash, redirect, url_for
from secret import secret_key

DATABASE = 'notes.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def make_notes(db_notes):
    notes = []
    for note in db_notes:
        note = dict(note)
        note['content'] = markdown.markdown(note['content'])
        notes.append(note)
    return notes


app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

@app.route('/')
def index():
    conn = get_db_connection()
    db_notes = conn.execute('SELECT id, created, content FROM notes;').fetchall()
    conn.close()

    notes = make_notes(db_notes)

    return render_template('index.html', notes=notes)
