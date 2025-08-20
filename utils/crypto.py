from __future__ import annotations
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os


def generate_key(num_bytes: int = 32) -> str:
	key = AESGCM.generate_key(bit_length=num_bytes * 8)
	return base64.urlsafe_b64encode(key).decode()


def encrypt(value: str, key_b64: str) -> str:
	key = base64.urlsafe_b64decode(key_b64)
	nonce = os.urandom(12)
	aesgcm = AESGCM(key)
	ciphertext = aesgcm.encrypt(nonce, value.encode(), None)
	return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def decrypt(token_b64: str, key_b64: str) -> str:
	key = base64.urlsafe_b64decode(key_b64)
	data = base64.urlsafe_b64decode(token_b64)
	nonce, ciphertext = data[:12], data[12:]
	aesgcm = AESGCM(key)
	plaintext = aesgcm.decrypt(nonce, ciphertext, None)
	return plaintext.decode()



