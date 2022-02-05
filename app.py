import sqlite3
import markdown
from flask import Flask, render_template, request, flash, redirect, url_for
from secret import secret_key
from init_db import DATABASE

def get_db_connection(db_file):
    conn = sqlite3.connect(db_file)
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
    conn = get_db_connection(DATABASE)
    db_notes = conn.execute('SELECT basename, title, created, content FROM notes;').fetchall()
    conn.close()
    notes = make_notes(db_notes)
    return render_template('index.html', notes=notes)
