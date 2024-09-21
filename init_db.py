# Initializes a sqlite datebase for a folder of Markdown files.
# See schema.sql for the tables in the database.
import sqlite3
import os
from note import read_note_path, Document, Entry
from datetime import datetime, timedelta
from pathlib import Path

TABLES = {
    "documents": "documents",
    "dates": "dates",
    "entries": "entries",
    "links_docs_dates": "links_docs_dates",
    "links_docs_docs": "links_docs_docs",
}


def init_tbl_documents(cursor: sqlite3.Cursor, documents: list[Document]):
    """Create `documents` table

    Args:
        cursor: sqlite3 Cursor
        documents: list of Documents
    """
    for doc in documents:
        relative_path = str(doc.path.parent).replace("\\", "/")
        cursor.execute(
            f"INSERT INTO {TABLES['documents']}(filename, date, relative_path) VALUES (?, ?, ?)",
            (doc.path.name, doc.date, relative_path),
        )


def init_tbl_dates(cursor: sqlite3.Cursor, dates: list[str]):
    """Create `dates` table

    Args:
        cursor: sqlite3 Cursor
        dates: list of dates
    """
    for date in dates:
        cursor.execute(f"INSERT INTO {TABLES['dates']}(date) VALUES (?)", (date,))


def init_tbl_entries(cursor: sqlite3.Cursor, entries: dict[Document, list[Entry]]):
    """Create `entries` table

    Args:
        cursor: sqlite3 Cursor
        entries: Document-Entry dictionary
    """
    for doc, entry_list in entries.items():
        results = cursor.execute(
            f"SELECT id FROM {TABLES['documents']} WHERE filename == :d",
            {"d": doc.path.name},
        ).fetchall()
        if results:
            doc_id = results[0][0]  # First result, first element in tuple (i.e. id).
            for entry in entry_list:
                cursor.execute(
                    f"INSERT INTO {TABLES['entries']}(doc_id, heading, content, date) VALUES (?, ?, ?, ?)",
                    (doc_id, entry.heading, entry.content, entry.date),
                )


def init_tbl_links_docs_dates(cursor: sqlite3.Cursor, links: dict[Document, list[str]]):
    """Create `links_docs_dates` table

    Args:
        cursor: sqlite3 Cursor
        links: Document-Date dictionary
    """
    for doc, dates in links.items():
        results = cursor.execute(
            f"SELECT id FROM {TABLES['documents']} WHERE filename == :d",
            {"d": doc.path.name},
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


def init_tbl_links_docs_docs(cursor: sqlite3.Cursor, links: dict[Document, list[str]]):
    """Create `links_docs_docs` table

    Args:
        cursor: sqlite3 Cursor
        links: Document-Links dictionary
    """
    for doc, to_files in links.items():
        from_file = doc.path.name
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
    """List dates between start and end

    Args:
        start: start date
        end: end date

    Returns:
        list of dates
    """
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    return [
        start_date + timedelta(days=x) for x in range(0, (end_date - start_date).days)
    ]


if __name__ == "__main__":
    import os
    import sys

    NOTES_PATH = Path(sys.argv[1])
    DB_PATH = Path(sys.argv[2]) if len(sys.argv) > 2 else "notes.db"
    SCHEMA_PATH = "schema.sql"
    MIN_DATE = "2000-01-01"
    MAX_DATE = str(datetime.now().date())

    docs, links_docs_dates, links_docs_docs, entries = read_note_path(NOTES_PATH)
    dates = [d.strftime("%Y-%m-%d") for d in make_dates_list(MIN_DATE, MAX_DATE)]

    with sqlite3.connect(DB_PATH) as db_conn:
        with open(SCHEMA_PATH) as f:
            db_conn.executescript(f.read())
        cursor = db_conn.cursor()
        init_tbl_dates(cursor, dates)
        db_conn.commit()
        init_tbl_documents(cursor, docs)
        db_conn.commit()
        init_tbl_entries(cursor, entries)
        db_conn.commit()
        init_tbl_links_docs_dates(cursor, links_docs_dates)
        db_conn.commit()
        init_tbl_links_docs_docs(cursor, links_docs_docs)
        db_conn.commit()
