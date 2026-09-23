"""Lecture 1: toy Diffie-Hellman key exchange.

Uses tiny numbers so the math is visible. Real deployments use 2048-bit+ groups
or elliptic curves (e.g. X25519). Do not use this code for anything real.

Run: python3 03_diffie_hellman.py
"""
import secrets

p = 23  # public prime modulus
g = 5   # public generator

a = secrets.randbelow(p - 2) + 1  # Alice's private key, never sent
b = secrets.randbelow(p - 2) + 1  # Bob's private key, never sent

A = pow(g, a, p)  # Alice sends A = g^a mod p over the open network
B = pow(g, b, p)  # Bob sends B = g^b mod p over the open network

s_alice = pow(B, a, p)  # (g^b)^a mod p
s_bob = pow(A, b, p)    # (g^a)^b mod p

print(f"public: p={p}, g={g}, A={A}, B={B}")
print(f"Alice computes s={s_alice}, Bob computes s={s_bob}, equal: {s_alice == s_bob}")
print("An eavesdropper sees p, g, A, B but must solve a discrete log to get a or b.")
