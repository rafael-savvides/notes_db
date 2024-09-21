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

    path: Path
    date: str = None


@dataclass
class Entry:
    """An entry in a markdown document.

    A markdown document is split into entries at markdown headings.
    An entry consists of:

    - heading: Markdown heading defined by one or more hash symbols (#) at the start of a line, followed by a space. The hashes are included in the heading.
        - If None, the entry has no heading. This happens if the first entry in a document has no headings.
    - content: Text between headings.
        - If "", then there is an empty line before the next heading.
        - If None, then the next heading is directly after.

    heading and content can't be both be None.
    """

    # TODO What if there are no headings? Should the default heading and content be ""?
    # What exactly is an entry? A subsection with a date?
    heading: str | None
    content: str | None
    date: str = None
    # TODO Add order? Else the document can't be reproduced. Maybe add the order in the db?
    # TODO Add heading level? Or it can be inferred from the string. And then it doesn't need to be removed and added when reconstructing the entry.


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


def header_lvl(line: str) -> int | None:
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
    """Parse Markdown text into Entries

    If no `#` is found, then ...?
    """
    lines = text.split("\n")
    lines_new = []
    accum = ""
    header = ""
    for line in lines:
        if header_lvl(line):
            e = Entry(heading=header, content=accum, date=guess_date(accum, header))
            if e.heading or e.content:
                lines_new.append(e)
            header = line
            accum = ""
        else:
            accum = accum + line
    lines_new.append(
        Entry(heading=header, content=accum, date=guess_date(accum, header))
    )
    return lines_new


def guess_date(content: str, header: str = None, regex: str = REGEX_DATE) -> str | None:
    """Guess the date of an entry

    Args:
        content: Text.
        header: Text header.
        regex: Date regular expression.

    Returns:
        The first date matching the regex, searched in the following order:

        - in `header`
        - at the start of `content`
        - after a newline in `content`
        - following `date:` in `content`

        None, if no date is found.
    """
    if header:
        date_in_header = re.search(regex, header)
        if date_in_header:
            return date_in_header.group()
    regex_cases = f"(^{regex})|((?<=\n){regex})|((?<=date:) ?{regex})"
    date_in_content = re.search(regex_cases, content)
    if date_in_content:
        return date_in_content.group().strip()
    return None
