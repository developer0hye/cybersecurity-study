"""Lecture 3: output escaping against XSS.

Run: python3 05_xss_escaping.py
"""
import html

user_input = "<script>alert('attack')</script>"

unsafe = f"<p>Results for {user_input}</p>"
safe = f"<p>Results for {html.escape(user_input)}</p>"

print("unsafe:", unsafe)  # a browser would run this script
print("safe:  ", safe)    # a browser shows the text instead of running it
