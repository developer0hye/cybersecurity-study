"""Lecture 1: plain hashing vs. salted, slow password hashing.

Run: python3 02_hash_and_salt.py
"""
import hashlib
import hmac
import os

password = "hunter2"

# 1. A plain, fast hash: two users with the same password get the same hash,
#    and an attacker can precompute (rainbow tables) or test billions per second.
print("sha256(alice):", hashlib.sha256(password.encode()).hexdigest())
print("sha256(bob):  ", hashlib.sha256(password.encode()).hexdigest())


# 2. A random salt per user plus a deliberately slow KDF (scrypt).
def hash_password(pw: str) -> tuple[bytes, bytes]:
    salt = os.urandom(16)
    digest = hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1)
    return salt, digest


def verify(pw: str, salt: bytes, digest: bytes) -> bool:
    candidate = hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(candidate, digest)  # constant-time comparison


alice = hash_password(password)
bob = hash_password(password)
print("\nscrypt(alice):", alice[0].hex(), alice[1].hex()[:32], "...")
print("scrypt(bob):  ", bob[0].hex(), bob[1].hex()[:32], "...")
print("same password, different stored values:", alice[1] != bob[1])
print("verify correct password:", verify("hunter2", *alice))
print("verify wrong password:  ", verify("hunter3", *alice))
