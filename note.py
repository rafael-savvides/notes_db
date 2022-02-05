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
        self.dates = extract_time(self.content, 'date')
        self.timestamps = extract_time(self.content, 'timestamp')
        self.folder = None #TODO
        self.yaml = parse_yaml(extract_yaml(self.content))
        self.title = self.__get_note_title__() # Is this method problematic? Calling self.
        self.datetime = self.__get_note_datetime__()
    
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

def read_note(filename):
    """Read markdown note into string."""
    with open(filename, encoding='utf8') as f:
        content = f.read()
    return content

def extract_time(text, format='date'):
    """Extract all timestamps of the form YYYY-MM-DD HH:MM:SS (format='timestamp') or YYYY-MM-DD (format='date'). 
    Return list of strings (unique and sorted)."""
    if format == 'date':
        regex = '\d\d\d\d-\d\d-\d\d'
    if format == 'timestamp':
        regex = '\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d'
    x = re.findall(regex, text)
    return list(set(x))

def parse_yaml(text):
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
