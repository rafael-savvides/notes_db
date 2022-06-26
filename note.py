from inspect import Attribute
import os
import yaml
import re
from mistletoe import Document
from bidict import bidict
import numpy as np
import re

class Note():
    """
    Stores metadata about a note.
    """
    def __init__(self, filename):
        self.name = os.path.basename(filename).replace('.md', '')
        self.content = read_note(filename) 
        self.yaml = parse_yaml(extract_yaml(self.content))
        self.dates = extract_time(self.content, 'date')
        self.timestamps = extract_time(self.content, 'timestamp')
        self.title = self.__get_note_title__() 
        self.datetime = self.__get_note_datetime__()
        self.filename = filename
        self.wiki_links = find_wiki_links(self.content)
    
    def __repr__(self) -> str:
        return f'Note({self.name})'

    def __get_note_title__(self):
        try: 
            title = self.yaml['title']
        except (KeyError, TypeError):
            try: 
                title = re.search('(?<=^# ).+', self.content).group(0).strip()
            except AttributeError:
                title = self.name
        return title
    
    def __get_note_datetime__(self):
        # Could be cleaned.
        try: 
            dt = self.yaml['date']
        except (KeyError, TypeError):
            try:
                # 3rd line is datetime in many notes
                dt = self.content.splitlines()[2]
                dt = extract_time(dt, format='timestamp')[0]
            except (TypeError, IndexError): 
                try: 
                    dt = min(self.timestamps)
                except (TypeError, ValueError):
                    try: 
                        dt = min(self.dates)
                    except (TypeError, ValueError):
                        dt = ''
        return dt

    def __len__(self):
        return len(self.content)


class NoteCollection():
    """
    Stores metadata about a collection of notes. 

    Examples:

    nc = NoteCollection()
    nc.lookup_table(13) # 'note13'
    nc.lookup_table.inverse('note13') # 13
    """

    def __init__(self, notes_path):
        self.notes = read_notes(notes_path) # List of notes. Could assign UID in each note.
        self.dir_structure = [] # Tree of Paths. 
        self.dates = []
        self.path_to_notes = notes_path
        self.path_to_figures = os.path.join(notes_path, 'figures') 
        self.lookup = bidict({id: name for id, name in zip(self.getattrs('id'), self.getattrs('name'))})
        self.note_links = make_adj_mat(self)

    def __repr__(self) -> str:
        return f'NoteCollection({len(self)})'

    def __len__(self):
        return len(self.notes)
    
    def getattrs(self, attr):
        return [getattr(note, attr) for note in self.notes]
    
    def get_backlinks(self, note: Note or str or int) -> list:
        if isinstance(note, Note):
            id = self.lookup.inverse[note.name]
        elif isinstance(note, str): 
            id = self.lookup.inverse[note]
        elif isinstance(note, int):
            id = note
        backlink_ids = np.nonzero(self.note_links[:, id])[0]
        return [self.notes[i] for i in backlink_ids]

class MultiNote(Note):
    """
    Note that contains multiple notes (e.g. about_x notes).
    """
    def __init__(self, filename):
        super().__init__(filename)

def read_note(filename):
    """Read markdown note into string."""
    with open(filename, encoding='utf8') as f:
        content = f.read()
    return content

def read_notes(notes_path: str) -> list:
    """Read all markdown files in a folder into a list of Note() objects."""
    note_path_list = [p for p in os.listdir(notes_path) if p.endswith('.md')]
    notes = []
    for i, note_name in enumerate(note_path_list):
        note_name_abs = os.path.join(notes_path, note_name)
        note = Note(note_name_abs)
        note.id = i
        notes.append(note)
    return notes

def extract_time(text, format='date') -> list:
    """Extract all timestamps of the form YYYY-MM-DD HH:MM:SS (format='timestamp') or YYYY-MM-DD (format='date'). 
    Return list of strings (unique and sorted)."""
    if format == 'date':
        regex = '\d\d\d\d-\d\d-\d\d'
    if format == 'timestamp':
        regex = '\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d'
    x = re.findall(regex, text)
    return list(set(x))

def parse_yaml(text) -> dict or None:
    """Parse YAML from string to dict."""
    return yaml.safe_load(text) if text else None

def extract_yaml(text):
    """Extract YAML block from text. YAML blocks are start and end with ---. 
    If multiple exist, returns first one. 
    If none exist, returns None."""
    try:
        y = re.search('(?<=^---)(.|\n)+(?=---)', text).group(0).strip()
    except AttributeError:
        return None
    return y

def parse_markdown_ast(txt):
    return Document(txt)

def find_wiki_links(text: str) -> list:
    """Find all [[wiki_links]] in a text."""
    regex = "(?<=\[\[)[a-zA-Z_]+(?=\]\])"
    x = re.findall(regex, text)
    return list(set(x))

def make_adj_mat(nc: NoteCollection) -> np.array:
    """Make adjacency matrix of links between notes in a NoteCollection.
    """
    n = len(nc)
    adj_mat = np.zeros((n, n))
    for from_note in nc.notes:
        from_id = nc.lookup.inverse[from_note.name]
        for to_note_name in from_note.wiki_links:
            if to_note_name in nc.getattrs('name'):
                to_id = nc.lookup.inverse[to_note_name]
                adj_mat[from_id, to_id] = 1
    return adj_mat
