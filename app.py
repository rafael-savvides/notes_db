from secret import secret_key
from init_db import DATABASE
import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for
import mistletoe
from mathjax import MathJaxRenderer

def get_db_connection(db_file):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def make_notes(db_notes):
    notes = []
    for note in db_notes:
        note = dict(note)
        note['content'] = mistletoe.markdown(note['content'], MathJaxRenderer)
        notes.append(note)
    return notes


app = Flask(__name__, static_folder='resources')
app.config['SECRET_KEY'] = secret_key

@app.route('/')
def index():
    conn = get_db_connection(DATABASE)
    db_notes = conn.execute('SELECT name, title, created, content FROM notes;').fetchall()
    conn.close()
    notes = make_notes(db_notes)
    # notes = notes[0:10]
    return render_template('index.html', notes=notes)

@app.route('/summary/', methods=('GET', 'POST'))
def summary():
    conn = get_db_connection(DATABASE)
    notes = conn.execute('SELECT name FROM notes;').fetchall()
    conn.close()
    return render_template('summary.html', notes=notes)
