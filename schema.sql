DROP TABLE IF EXISTS dates;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS links_docs_dates;
DROP TABLE IF EXISTS links_docs_docs;

CREATE TABLE dates (
	id INTEGER PRIMARY KEY AUTOINCREMENT, 
	date TIMESTAMP NOT NULL 
);

CREATE TABLE documents (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	filename TEXT NOT NULL, 
	date TIMESTAMP,
	relative_path TEXT NOT NULL
);

CREATE TABLE entries (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	doc_id INTEGER NOT NULL, 
	header TEXT,
	content TEXT,
	date TIMESTAMP,
	FOREIGN KEY (doc_id) REFERENCES documents (id)
);

CREATE TABLE links_docs_dates (
	id INTEGER PRIMARY KEY AUTOINCREMENT, 
	doc_id INTEGER NOT NULL,
	date_id INTEGER NOT NULL,
	FOREIGN KEY (doc_id) REFERENCES documents (id),
	FOREIGN KEY (date_id) REFERENCES dates (id)
);

CREATE TABLE links_docs_docs (
	id INTEGER PRIMARY KEY AUTOINCREMENT, 
	from_doc_id INTEGER NOT NULL,
	to_doc_id INTEGER NOT NULL,
	FOREIGN KEY (from_doc_id) REFERENCES documents (id),
	FOREIGN KEY (to_doc_id) REFERENCES documents (id)
);
