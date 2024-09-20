import os
import re
from dataclasses import dataclass
import re
from pathlib import Path

REGEX_TIMESTAMP = "\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d"
REGEX_DATE = "\d\d\d\d-\d\d-\d\d"
REGEX_MDLINK = "(?<=\]\()[a-zA-Z0-9_\/\.]+\.md(?=\))"


@dataclass(frozen=True, eq=True)
class Document:
    """A markdown document."""

    path: str | Path
    date: str = None


@dataclass
class Entry:
    """An entry in a markdown document."""

    # TODO What if there are no headers? Should the default header and content be ""?
    header: str
    content: str
    date: str = None


def read_note_path(
    path: str,
) -> tuple[
    list[Document],
    dict[Document, list[str]],
    dict[Document, list[str]],
    dict[Document, list[Entry]],
]:
    """Read all Markdown files in a folder

    Args:
        path: Path to a folder with Markdown files.

    Returns:
        - a list of Documents
        - an adjacency list {Document: [dates]}
        - an adjacency list {Document: [md_links]}
        - a dict of Entries, {Document: [Entries]}
    """
    files = list(Path(path).glob("**/*.md"))
    docs = []
    links_docs_dates = {}
    links_docs_docs = {}
    entries = {}
    for file in files:
        with open(file, encoding="utf8") as f:
            content = f.read()
        date = guess_date(content)
        # Using relative filename instead of basename to ensure unique keys.
        relative_filepath = Path(str(file.relative_to(path)).replace("\\", "/"))
        doc = Document(path=relative_filepath, date=date)
        entries[doc] = parse_to_entries(content)
        links_docs_dates[doc] = list(set(re.findall(REGEX_DATE, content)))
        links_docs_docs[doc] = list(set(re.findall(REGEX_MDLINK, content)))
        docs.append(doc)
    return docs, links_docs_dates, links_docs_docs, entries


def header_lvl(x: str) -> int | None:
    """Count how many # are at the start of the line."""
    r = re.search("^#+ ", x)
    return r.span()[1] if r else None


def parse_to_entries(text: str) -> list[Entry]:
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
