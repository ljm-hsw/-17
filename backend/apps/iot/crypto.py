import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


def encrypt_device_secret(secret: str) -> str:
    fernet = Fernet(settings.DEVICE_SECRET_ENCRYPTION_KEY.encode())
    return fernet.encrypt(secret.encode()).decode()


def decrypt_device_secret(ciphertext: str) -> str:
    fernet = Fernet(settings.DEVICE_SECRET_ENCRYPTION_KEY.encode())
    return fernet.decrypt(ciphertext.encode()).decode()


def fingerprint_device_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()[:16]
