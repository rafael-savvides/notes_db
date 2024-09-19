# Notes UI

Serve a folder of markdown files as a Flask app.

```bash
pipenv install 
pipenv shell

python init_db.py # Update the sqlite database.

./run_app.sh # Run Flask app.
```

Set up `config.json` to have: 

- `path_to_notes`: path to folder including markdown files to be served

Environment variables: 

- `SECRET_KEY`: required by Flask for signing cookies.
- `PATH_TO_MATHJAX_JS`: (optional) path to MathJax.js to render Latex. The path should be in the `static_folder` defined in `Flask()`. If missing, uses MathJax CDN from the web.
