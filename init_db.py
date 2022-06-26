# Initializes a sqlite datebase for a folder of Markdown files.
# See SCHEMA for the tables in the database.
import sqlite3
import os
from secret import notes_path
from note import read_note_path, Document
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

ROOT_PATH = notes_path
DATABASE = 'notes.db'
SCHEMA = 'schema.sql'
MIN_DATE = "2014-01-01"
MAX_DATE = str(datetime.now().date())

TBL_DOCS = 'documents'
TBL_DATES = 'dates'
TBL_DOCS2DATES = 'links_docs_dates'
TBL_DOCS2DOCS = 'links_docs_docs'

def init_db_documents(cursor, documents: List[Document]):
    for doc in documents:
        cursor.execute(
            f"INSERT INTO {TBL_DOCS}(filename, date) VALUES (?, ?)", 
            (doc.filename, doc.date))

def init_db_dates(cursor, dates: List[str]):
    for date in dates:
        cursor.execute(f"INSERT INTO {TBL_DATES}(date) VALUES (?)", (date,))

def init_db_links_docs_dates(cursor, links: Dict[str, List[str]]):
    for filename, dates in links.items():
        res = cursor.execute(f"SELECT id FROM {TBL_DOCS} WHERE filename == :d", {'d': filename}).fetchall()
        if res:
            doc_id = res[0][0] # First result, first element (i.e. id). 
        for date in dates:
            res = cursor.execute(f"SELECT id FROM {TBL_DATES} WHERE date == :d", {'d': date}).fetchall()
            if res:
                date_id = res[0][0]
                cursor.execute(f"INSERT INTO {TBL_DOCS2DATES}(doc_id, date_id) VALUES (?,?)", (doc_id, date_id))

def init_db_links_docs_docs(cursor, links: Dict[str, List[str]]):
    for from_file, to_files in links.items():
        res = cursor.execute(f"SELECT id FROM {TBL_DOCS} WHERE filename == :d", {'d': from_file}).fetchall()
        if res:
            from_doc_id = res[0][0] # First result, first element (i.e. id).
        for to_file in to_files:
            #TODO Check if link contains .md, and add it if not.
            res = cursor.execute(f"SELECT id FROM {TBL_DOCS} WHERE filename == :d", {'d': to_file}).fetchall()
            if res:
                to_doc_id = res[0][0]
                cursor.execute(f"INSERT INTO {TBL_DOCS2DOCS}(from_doc_id, to_doc_id) VALUES (?,?)", (from_doc_id, to_doc_id))

def make_dates_list(start: str, end: str):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    return [start_date + timedelta(days=x) for x in range(0, (end_date-start_date).days)]

if __name__ == "__main__": 
    docs, links_docs_dates, links_docs_docs = read_note_path(ROOT_PATH)
    dates = [d.strftime('%Y-%m-%d') for d in make_dates_list(MIN_DATE, MAX_DATE)]

    db_connection = sqlite3.connect(DATABASE)
    with open(SCHEMA) as f:
        db_connection.executescript(f.read())
    cursor = db_connection.cursor()
    init_db_dates(cursor, dates)
    db_connection.commit()
    init_db_documents(cursor, docs)
    db_connection.commit() 
    init_db_links_docs_dates(cursor, links_docs_dates)
    db_connection.commit()
    init_db_links_docs_docs(cursor, links_docs_docs)
    db_connection.commit()
    db_connection.close()
    