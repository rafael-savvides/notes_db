import os
import re
from mistletoe import Document
from dataclasses import dataclass
from typing import List, Tuple
import re

TIMESTAMP_REGEX = '\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d'
DATE_REGEX = '\d\d\d\d-\d\d-\d\d'

@dataclass
class Entry():
    header: str
    content: str
    date: str = None

@dataclass
class Document():
    filename: str
    created: str = None

def read_documents(path: str) -> List[Document]:
    """Read all markdown files in a folder into a list of Documents."""
    #TODO Make recursive.
    files = [p for p in os.listdir(path) if p.endswith('.md')]
    docs = []
    for file in files:
        file_abs = os.path.join(path, file)
        with open(file_abs, encoding='utf8') as f:
            content = f.read()
        date = guess_date(content)
        doc = Document(filename=file, created=date)
        docs.append(doc)
    return docs

def header_lvl(x: str) -> int or None: 
    """Count how many # are at the start of the line."""
    r = re.search('^#+ ', x)
    return r.span()[1] if r else None

def parse_to_entries(lines: List[str]) -> List[Entry]:
    """Parse Markdown text into (header, contents)."""
    lines_new = []
    accum = ''
    header = ''
    for line in lines:
        if header_lvl(line):
            lines_new.append(Entry(header, accum, guess_date(accum, header)))
            header = line
            accum = ''
        else:
            accum = accum + line
    lines_new.append(Entry(header, accum)) 
    return lines_new

def guess_date(content: str, header: str = None):
    """Guess the date of an entry"""
    if header:
        ts_in_header = re.match(TIMESTAMP_REGEX, header)
        if ts_in_header:
            return ts_in_header.group()
        date_in_header = re.match(DATE_REGEX, header)
        if date_in_header:
            return date_in_header.group()
    ts_in_content = re.search(f'(^{TIMESTAMP_REGEX})|(\n{TIMESTAMP_REGEX})', content)
    if ts_in_content:
        return ts_in_content.group()
    date_in_content = re.search(f'(^{DATE_REGEX})|(\n{DATE_REGEX})', content)
    if date_in_content:
        return date_in_content.group()
    return None
