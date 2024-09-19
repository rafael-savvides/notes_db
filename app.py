import os
import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for
import mistletoe
from mathjax import MathJaxRenderer

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "asdf"
)  # Required by Flask to sign cookies.

DB_PATH = os.getenv("NOTES_DB_PATH", "notes.db")


def get_db_connection(db_file):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


def make_notes(db_notes):
    notes = []
    for note in db_notes:
        note = dict(note)
        note["content"] = mistletoe.markdown(note["content"], MathJaxRenderer)
        notes.append(note)
    return notes


# TODO Fix queries below. Change notes to documents, name to filename. title doesnt exist.
@app.route("/")
def index():
    conn = get_db_connection(DB_PATH)
    db_notes = conn.execute(
        "SELECT name, title, created, content FROM notes;"
    ).fetchall()
    conn.close()
    notes = make_notes(db_notes)
    # notes = notes[0:10]
    return render_template("index.html", notes=notes)


@app.route("/summary/", methods=("GET", "POST"))
def summary():
    conn = get_db_connection(DB_PATH)
    notes = conn.execute("SELECT name FROM notes;").fetchall()
    conn.close()
    return render_template("summary.html", notes=notes)


@app.route("/dates/", methods=("GET", "POST"))
def dates():
    # TODO Fix the query (or db?). The dates and notes are misaligned (e.g. says k-means is 2019-08-03 but is 2020-12-18)
    query = """select notes.name, notes.content, notes.title, dates.date from dates 
    inner join notes_dates on dates.id=notes_dates.date_id 
    inner join notes on notes_dates.note_id = notes.id 
    order by date;
    """
    conn = get_db_connection(DB_PATH)
    dates_notes = conn.execute(query).fetchall()
    conn.close()
    return render_template("dates.html", dates=dates_notes)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
