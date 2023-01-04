import os
import re
from mistletoe import Document
from dataclasses import dataclass
from typing import List, Tuple
import re
from pathlib import Path

REGEX_TIMESTAMP = "\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d"
REGEX_DATE = "\d\d\d\d-\d\d-\d\d"
REGEX_WIKILINK = "(?<=\[\[)[a-zA-Z_]+(?=\]\])"


@dataclass
class Entry:
    header: str
    content: str
    date: str = None


@dataclass
class Document:
    filename: str
    date: str = None


def read_note_path(path: str) -> Tuple[List[Document], List[str], List[str]]:
    """Read all Markdown files in a folder into a list of Documents, an adjacency list to dates, and an adjacency list to other Documents."""
    files = list(Path(path).glob("**/*.md"))
    docs = []
    links_docs_dates = {}
    links_docs_docs = {}
    entries = {}
    for file in files:
        content = read_file(file)
        date = guess_date(content)
        doc = Document(
            filename=str(file.relative_to(path)).replace("\\", "/"), date=date
        )
        # Using relative filename instead of basename to ensure unique keys.
        entries[doc.filename] = parse_to_entries(content)
        links_docs_dates[doc.filename] = find_dates(content)
        links_docs_docs[doc.filename] = [
            add_extension(x, ".md") for x in find_wiki_links(content)
        ]
        docs.append(doc)
    return docs, links_docs_dates, links_docs_docs, entries


def read_file(file: str, path: str = None):
    file = os.path.join(path, file) if path else file
    with open(file, encoding="utf8") as f:
        content = f.read()
    return content


def header_lvl(x: str) -> int or None:
    """Count how many # are at the start of the line."""
    r = re.search("^#+ ", x)
    return r.span()[1] if r else None


def parse_to_entries(text: str) -> List[Entry]:
    """Parse Markdown text into (header, contents)."""
    lines = text.split("\n")
    lines_new = []
    accum = ""
    header = ""
    for line in lines:
        if header_lvl(line):
            e = Entry(header, accum, guess_date(accum, header))
            if e.header or e.content:
                lines_new.append(e)
            header = line
            accum = ""
        else:
            accum = accum + line
    lines_new.append(Entry(header, accum, guess_date(accum, header)))
    return lines_new


def guess_date(content: str, header: str = None, regex: str = REGEX_DATE):
    """Guess the date of an entry. Uses the first occurring date that begins a line."""
    # TODO Compile regex outside the function.
    if header:
        date_in_header = re.search(regex, header)
        if date_in_header:
            return date_in_header.group()
    regex_cases = f"(^{regex})|((?<=\n){regex})|((?<=date:) ?{regex})"
    date_in_content = re.search(regex_cases, content)
    if date_in_content:
        return date_in_content.group().strip()
    return None


def find_dates(text: str) -> List[str]:
    """Find all dates in a text."""
    x = re.findall(REGEX_DATE, text)
    return list(set(x))


def find_wiki_links(text: str) -> List[str]:
    """Find all [[wiki_links]] in a text."""
    x = re.findall(REGEX_WIKILINK, text)
    return list(set(x))


def add_extension(x: str, ext: str):
    """Append a file extension to a filename, if it already does not have it."""
    return x if x.endswith(ext) else x + ext


def basename(x: str):
    return Path(x).name
