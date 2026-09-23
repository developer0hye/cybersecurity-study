"""Lecture 3: command injection with a shell vs. passing an argument list.

Run: python3 06_command_injection.py  (Linux/macOS)
"""
import subprocess

filename = "notes.txt; echo INJECTED: this command should never have run"

print("--- VULNERABLE: shell=True with string formatting ---", flush=True)
subprocess.run(f"echo listing {filename}", shell=True)

print("--- SAFE: argument list, no shell ---", flush=True)
subprocess.run(["echo", "listing", filename])  # the whole string is one argument
