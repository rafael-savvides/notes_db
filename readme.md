# Notes UI


# Flask App

Run like this: 

```bash
./run_app.sh
```

Set up `secret.py` to have: 

- `notes_path`: path to folder including markdown files to be served
- `secret_key`: any secret string 
- `path_to_mathjax_js`: (optional) path to MathJax.js (the path should be in the `static_folder` defined in `Flask()`). If missing, uses MathJax CDN from the web to render Latex.

# SQLite database

Update the database by running `init_db.py`.