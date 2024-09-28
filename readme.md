# Notes db

Make a sqlite database of markdown files.

```bash
pipenv install 
pipenv shell

python init_db.py [path_to_notes] [path_to_notes_db]
```

where

- `path_to_notes`: path to folder including markdown files to be served
- `path_to_notes_db`: (optional) path to sqlite database. Defaults to `notes.db`.
