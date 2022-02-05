import sqlite3
import markdown
from flask import Flask, render_template, request, flash, redirect, url_for

DATABASE = 'notes.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this should be a secret random string'


@app.route('/')
def index():
    conn = get_db_connection()
    db_notes = conn.execute('SELECT id, created, content FROM notes;').fetchall()
    conn.close()

    notes = []
    for note in db_notes:
       note = dict(note)
       note['content'] = markdown.markdown(note['content'])
       notes.append(note)

    return render_template('index.html', notes=notes)
