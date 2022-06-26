# Initializes a sqlite datebase for a folder of Markdown files.
# See SCHEMA for the tables in the database.
import sqlite3
import os
from secret import path_to_notes
from note import read_note_path, Document, Entry, basename
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from pathlib import Path

ROOT_PATH = path_to_notes
DATABASE = 'notes.db'
SCHEMA = 'schema.sql'
MIN_DATE = "2014-01-01"
MAX_DATE = str(datetime.now().date())

TBL_DOCS = 'documents'
TBL_DATES = 'dates'
TBL_ENTRIES = 'entries'
TBL_DOCS2DATES = 'links_docs_dates'
TBL_DOCS2DOCS = 'links_docs_docs'

def init_db_documents(cursor, documents: List[Document]):
    for doc in documents:
        filename = basename(doc.filename)
        relative_path = str(Path(doc.filename).parent).replace('\\', '/')
        cursor.execute(
            f"INSERT INTO {TBL_DOCS}(filename, date, relative_path) VALUES (?, ?, ?)", 
            (filename, doc.date, relative_path))

def init_db_dates(cursor, dates: List[str]):
    for date in dates:
        cursor.execute(f"INSERT INTO {TBL_DATES}(date) VALUES (?)", (date,))

def init_db_entries(cursor, entries: Dict[str, List[Entry]]):
    for filename, entry_list in entries.items():
        filename = basename(filename)
        results = cursor.execute(f"SELECT id FROM {TBL_DOCS} WHERE filename == :d", {'d': filename}).fetchall()
        if results:
            doc_id = results[0][0] # First result, first element in tuple (i.e. id). 
            for entry in entry_list:
                cursor.execute(f"INSERT INTO {TBL_ENTRIES}(doc_id, header, content, date) VALUES (?, ?, ?, ?)", 
                (doc_id, entry.header, entry.content, entry.date))

def init_db_links_docs_dates(cursor, links: Dict[str, List[str]]):
    for filename, dates in links.items():
        filename = basename(filename)
        results = cursor.execute(f"SELECT id FROM {TBL_DOCS} WHERE filename == :d", {'d': filename}).fetchall()
        if results:
            doc_id = results[0][0] # First result, first element in tuple (i.e. id). 
            for date in dates:
                results = cursor.execute(f"SELECT id FROM {TBL_DATES} WHERE date == :d", {'d': date}).fetchall()
                if results:
                    date_id = results[0][0]
                    cursor.execute(f"INSERT INTO {TBL_DOCS2DATES}(doc_id, date_id) VALUES (?,?)", (doc_id, date_id))

def init_db_links_docs_docs(cursor, links: Dict[str, List[str]]):
    for from_file, to_files in links.items():
        from_file = basename(from_file)
        results = cursor.execute(f"SELECT id FROM {TBL_DOCS} WHERE filename == :d", {'d': from_file}).fetchall()
        if results:
            from_doc_id = results[0][0] # First result, first element in tuple (i.e. id).
            for to_file in to_files:
                results = cursor.execute(f"SELECT id FROM {TBL_DOCS} WHERE filename == :d", {'d': to_file}).fetchall()
                if results:
                    to_doc_id = results[0][0]
                    cursor.execute(f"INSERT INTO {TBL_DOCS2DOCS}(from_doc_id, to_doc_id) VALUES (?,?)", (from_doc_id, to_doc_id))

def make_dates_list(start: str, end: str):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    return [start_date + timedelta(days=x) for x in range(0, (end_date-start_date).days)]

if __name__ == "__main__": 
    docs, links_docs_dates, links_docs_docs, entries = read_note_path(ROOT_PATH)
    dates = [d.strftime('%Y-%m-%d') for d in make_dates_list(MIN_DATE, MAX_DATE)]

    db_connection = sqlite3.connect(DATABASE)
    with open(SCHEMA) as f:
        db_connection.executescript(f.read())
    cursor = db_connection.cursor()
    init_db_dates(cursor, dates)
    db_connection.commit()
    init_db_documents(cursor, docs)
    db_connection.commit() 
    init_db_entries(cursor, entries)
    db_connection.commit() 
    init_db_links_docs_dates(cursor, links_docs_dates)
    db_connection.commit()
    init_db_links_docs_docs(cursor, links_docs_docs)
    db_connection.commit()
    db_connection.close()
    