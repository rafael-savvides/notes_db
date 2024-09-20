# Notes db

Make a sqlite database of markdown files.

```bash
pipenv install 
pipenv shell

python init_db.py 
```

Set up `config.json` to have: 

- `path_to_notes`: path to folder including markdown files to be served



# TODO

- explain what markdown files (entries, links between files)
    - add examples markdown files?
    - explain reasoning for db, to browse entries by date in a db browser
- remove pipfile, use venv? need just python stdlib
- use context managers in init_db
    - maybe they didnt work when passing the cursor to a fn
- rename `read_note_path`
