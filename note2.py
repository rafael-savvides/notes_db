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
    date: str = None

def read_note_path(path: str) -> Tuple[List[Document], List[str], List[str]]:
    """Read all Markdown files in a folder into a list of Documents, an adjacency list to dates, and an adjacency list to other Documents."""
    #TODO Make recursive.
    files = [p for p in os.listdir(path) if p.endswith('.md')]
    docs = []
    links_docs_dates = {}
    links_docs_docs = {}
    for file in files:
        content = read_file(file, path)
        date = guess_date(content)
        doc = Document(filename=file, date=date)
        links_docs_dates[doc.filename] = find_dates(content)
        links_docs_docs[doc.filename] = find_wiki_links(content)
        docs.append(doc)
    return docs, links_docs_dates, links_docs_docs

def read_file(file: str, path: str = None):
    file = os.path.join(path, file) if path else file
    with open(file, encoding='utf8') as f:
        content = f.read()
    return content

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

def guess_date(content: str, header: str = None, regex: str = DATE_REGEX):
    """Guess the date of an entry. Uses the first occurring date that begins a 
    line."""
    #TODO Compile regex outside the function.
    #TODO Simplify
    if header:
        date_in_header = re.match(regex, header)
        if date_in_header:
            return date_in_header.group()
    date_in_content = re.search(f'(^{regex})|(\n{regex})', content)
    if date_in_content:
        return date_in_content.group().replace('\n', '')
    return None

def find_dates(text: str) -> List[str]:
    """Make a list of all dates in a text."""
    x = re.findall(DATE_REGEX, text)
    return list(set(x))

def find_wiki_links(text: str) -> List[str]:
    """Find all [[wiki_links]] in a text."""
    regex = "(?<=\[\[)[a-zA-Z_]+(?=\]\])"
    x = re.findall(regex, text)
    return list(set(x))
