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
    """A markdown document.

    Attributes:
        path: the document's path relative to a root folder
        date: document date
    """

    path: Path
    date: str = None


@dataclass
class Entry:
    """An entry in a markdown document.

    A markdown document is split into entries at markdown headings.

    Attributes:
        heading: Markdown heading defined by one or more hash symbols (#) at the start of a line, followed by a space. The hashes are included in the heading.
            - If None, the entry has no heading. This happens if the first entry in a document has no headings.
        content: Text between headings.
            - If "", then there is an empty line before the next heading.
            - If None, then the next heading is directly after.
        date: entry date
        position: the position of the entry inside the document.

    Notes:

    - heading and content can't be both be None.
    - A document can be reconstructed by sorting its entries by their position and printing their heading and content.
    """

    heading: str | None
    content: str | None
    position: int
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


def heading_lvl(line: str) -> int | None:
    """Count hash characters (#) at the start of a string.

    Args:
        line: string

    Returns:
        number of # characters in the beginning of line
        or None if no #
    #TODO Why not return zero if no #?
    """
    r = re.search("^#+ ", line)
    return r.span()[1] if r else None


def parse_to_entries(text: str) -> list[Entry]:
    """Parse Markdown text into Entries"""
    # TODO ensure position works as intended.
    lines = text.split("\n")
    lines_new = []
    accum = ""
    heading = ""
    position = 0
    for line in lines:
        if heading_lvl(line):
            e = Entry(
                heading=heading,
                content=accum,
                position=position,
                date=guess_date(accum, heading),
            )
            if e.heading or e.content:
                lines_new.append(e)
            heading = line
            accum = ""
            position += 1
        else:
            accum = accum + line
    lines_new.append(
        Entry(
            heading=heading,
            content=accum,
            position=position,
            date=guess_date(accum, heading),
        )
    )
    return lines_new


def guess_date(
    content: str, heading: str = None, regex: str = REGEX_DATE
) -> str | None:
    """Guess the date of an entry

    Args:
        content: Text.
        heading: Text heading.
        regex: Date regular expression.

    Returns:
        The first date matching the regex, searched in the following order:

        - in `heading`
        - at the start of `content`
        - after a newline in `content`
        - following `date:` in `content`

        None, if no date is found.
    """
    if heading:
        date_in_heading = re.search(regex, heading)
        if date_in_heading:
            return date_in_heading.group()
    regex_cases = f"(^{regex})|((?<=\n){regex})|((?<=date:) ?{regex})"
    date_in_content = re.search(regex_cases, content)
    if date_in_content:
        return date_in_content.group().strip()
    return None
