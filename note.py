from inspect import Attribute
import os
import yaml
import re

class Note():
    """
    Stores metadata about a note e.g. content, filename, folder, timestamps.
    """
    def __init__(self, filename):
        self.content = read_note(filename) 
        self.basename = os.path.basename(filename).replace('.md', '')
        self.filename = filename
        self.length = len(self.content)
        self.timestamps = extract_timestamps(self.content)
        self.folder = None #TODO
        self.yaml = parse_yaml(extract_yaml(self.content))
        self.title = self.__get_note_title__() # Is this method problematic? Calling self.
    
    def __repr__(self) -> str:
        return f'Note\nName: {self.basename}\nLength: {self.length}'

    def __get_note_title__(self):
        try: 
            title = self.yaml['title']
        except (KeyError, TypeError):
            try: 
                title = re.search('(?<=^# ).+', self.content).group(0).strip()
            except AttributeError:
                title = self.basename
        return title

def read_note(filename):
    """Read markdown note into string."""
    with open(filename, encoding='utf8') as f:
        content = f.read()
    return content

def extract_timestamps(text):
    """Extract all timestamps of the form YYYY-MM-DD HH:MM:SS or YYYY-MM-DD. 
    Return list."""
    timestamps = re.findall('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', text)
    dates = re.findall('\d\d\d\d-\d\d-\d\d', text)
    #TODO Ensure dates are not duplicated in timestamps. maybe return tuple of both entities?
    found = dates + timestamps
    return found

def parse_yaml(text):
    """Parse YAML from string to dict."""
    return yaml.safe_load(text) if text else None

def extract_yaml(text):
    """Extract YAML block from text. YAML blocks are start and end with ---. 
    If multiple exist, returns first one. 
    If none exist, returns None."""
    try:
        y = re.search('(?<=---)(.|\n)+(?=---)', text).group(0).strip()
    except AttributeError:
        return None
    return y
