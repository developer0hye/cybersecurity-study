"""Lecture 0: how the size of the character set and the length change brute-force cost.

Run: python3 01_keyspace.py
"""
from string import ascii_letters, digits, punctuation

GUESSES_PER_SECOND = 10_000_000_000  # an offline attacker with GPUs against a fast hash

CHARSETS = {
    "digits": digits,
    "letters": ascii_letters,
    "letters+digits+punctuation": ascii_letters + digits + punctuation,
}


def human(seconds: float) -> str:
    for unit, size in (("years", 31_536_000), ("days", 86_400), ("hours", 3_600), ("minutes", 60)):
        if seconds >= size:
            return f"{seconds / size:,.1f} {unit}"
    return f"{seconds:,.3f} seconds"


for name, charset in CHARSETS.items():
    for length in (4, 8, 12, 16):
        space = len(charset) ** length
        print(f"{name:28} len={length:2}  {space:.3e} combinations  worst case {human(space / GUESSES_PER_SECOND)}")
    print()
