"""Lecture 3: SQL injection and why parameterized queries fix it.

Run: python3 04_sql_injection.py
"""
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (username TEXT, password TEXT)")
db.executemany("INSERT INTO users VALUES (?, ?)", [("malan", "secret"), ("admin", "s3cr3t")])

username, password = "malan", "' OR '1'='1"

# VULNERABLE: user input is pasted into the SQL text, so it can change the query's structure.
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
print("query:", query)
print("vulnerable result:", db.execute(query).fetchall())

# SAFE: the query structure is fixed; the input is sent separately as data.
safe = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchall()
print("parameterized result:", safe)
