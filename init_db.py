# Initializes a sqlite datebase for a folder of Markdown files.
# See schema.sql for the tables in the database.
import sqlite3
import os
from note import read_note_path, Document, Entry, basename
from datetime import datetime, timedelta
from pathlib import Path

TABLES = {
    "documents": "documents",
    "dates": "dates",
    "entries": "entries",
    "links_docs_dates": "links_docs_dates",
    "links_docs_docs": "links_docs_docs",
}


def init_db_documents(cursor, documents: list[Document]):
    for doc in documents:
        filename = basename(doc.filename)
        relative_path = str(Path(doc.filename).parent).replace("\\", "/")
        cursor.execute(
            f"INSERT INTO {TABLES['documents']}(filename, date, relative_path) VALUES (?, ?, ?)",
            (filename, doc.date, relative_path),
        )


def init_db_dates(cursor, dates: list[str]):
    for date in dates:
        cursor.execute(f"INSERT INTO {TABLES['dates']}(date) VALUES (?)", (date,))


def init_db_entries(cursor, entries: dict[str, list[Entry]]):
    for filename, entry_list in entries.items():
        filename = basename(filename)
        results = cursor.execute(
            f"SELECT id FROM {TABLES['documents']} WHERE filename == :d",
            {"d": filename},
        ).fetchall()
        if results:
            doc_id = results[0][0]  # First result, first element in tuple (i.e. id).
            for entry in entry_list:
                cursor.execute(
                    f"INSERT INTO {TABLES['entries']}(doc_id, header, content, date) VALUES (?, ?, ?, ?)",
                    (doc_id, entry.header, entry.content, entry.date),
                )


def init_db_links_docs_dates(cursor, links: dict[str, list[str]]):
    for filename, dates in links.items():
        filename = basename(filename)
        results = cursor.execute(
            f"SELECT id FROM {TABLES['documents']} WHERE filename == :d",
            {"d": filename},
        ).fetchall()
        if results:
            doc_id = results[0][0]  # First result, first element in tuple (i.e. id).
            for date in dates:
                results = cursor.execute(
                    f"SELECT id FROM {TABLES['dates']} WHERE date == :d", {"d": date}
                ).fetchall()
                if results:
                    date_id = results[0][0]
                    cursor.execute(
                        f"INSERT INTO {TABLES['links_docs_dates']}(doc_id, date_id) VALUES (?,?)",
                        (doc_id, date_id),
                    )


def init_db_links_docs_docs(cursor, links: dict[str, list[str]]):
    for from_file, to_files in links.items():
        from_file = basename(from_file)
        results = cursor.execute(
            f"SELECT id FROM {TABLES['documents']} WHERE filename == :d",
            {"d": from_file},
        ).fetchall()
        if results:
            from_doc_id = results[0][
                0
            ]  # First result, first element in tuple (i.e. id).
            for to_file in to_files:
                results = cursor.execute(
                    f"SELECT id FROM {TABLES['documents']} WHERE filename == :d",
                    {"d": to_file},
                ).fetchall()
                if results:
                    to_doc_id = results[0][0]
                    cursor.execute(
                        f"INSERT INTO {TABLES['links_docs_docs']}(from_doc_id, to_doc_id) VALUES (?,?)",
                        (from_doc_id, to_doc_id),
                    )


def make_dates_list(start: str, end: str):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    return [
        start_date + timedelta(days=x) for x in range(0, (end_date - start_date).days)
    ]


if __name__ == "__main__":
    import json

    with open("config.json") as f:
        config = json.load(f)

    SCHEMA_PATH = "schema.sql"
    DB_PATH = os.getenv("NOTES_DB_PATH", "notes.db")

    NOTES_PATH = config["path_to_notes"]
    MIN_DATE = config["min_date"]
    MAX_DATE = (
        config["max_date"] if config["max_date"] != "" else str(datetime.now().date())
    )

    docs, links_docs_dates, links_docs_docs, entries = read_note_path(NOTES_PATH)
    dates = [d.strftime("%Y-%m-%d") for d in make_dates_list(MIN_DATE, MAX_DATE)]

    db_conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        db_conn.executescript(f.read())
    cursor = db_conn.cursor()
    init_db_dates(cursor, dates)
    db_conn.commit()
    init_db_documents(cursor, docs)
    db_conn.commit()
    init_db_entries(cursor, entries)
    db_conn.commit()
    init_db_links_docs_dates(cursor, links_docs_dates)
    db_conn.commit()
    init_db_links_docs_docs(cursor, links_docs_docs)
    db_conn.commit()
    db_conn.close()
