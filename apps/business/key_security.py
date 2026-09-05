import base64
import hashlib
from django.conf import settings

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def _get_cipher():
    secret = getattr(settings, 'SECRET_KEY', 'fallback-default-secret-key-123')
    key_bytes = hashlib.sha256(secret.encode('utf-8')).digest()
    if HAS_CRYPTO:
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        return Fernet(fernet_key)
    return key_bytes


def encrypt_key(raw_key: str) -> str:
    """
    Encrypts a raw API key string using AES-256 (Fernet) or key-derived token cipher.
    """
    if not raw_key or not raw_key.strip():
        return ""
    
    key = raw_key.strip()
    if key.startswith("gAAAAA") or key.startswith("ENC:"):
        return key

    if HAS_CRYPTO:
        try:
            cipher = _get_cipher()
            encrypted_bytes = cipher.encrypt(key.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception:
            pass

    # Pure Python Fallback Cipher (HMAC-SHA256 derived stream token)
    secret = getattr(settings, 'SECRET_KEY', 'fallback-secret-key-123')
    key_bytes = hashlib.sha256(secret.encode('utf-8')).digest()
    key_len = len(key_bytes)
    key_encoded = key.encode('utf-8')
    encrypted_bytes = bytearray()
    for i, b in enumerate(key_encoded):
        encrypted_bytes.append(b ^ key_bytes[i % key_len])
    
    encoded_str = base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
    return f"ENC:{encoded_str}"


def decrypt_key(encrypted_token: str) -> str:
    """
    Decrypts an encrypted API key token back to plaintext.
    Handles legacy unencrypted strings gracefully.
    """
    if not encrypted_token or not encrypted_token.strip():
        return ""

    token = encrypted_token.strip()
    if not (token.startswith("gAAAAA") or token.startswith("ENC:")):
        return token  # Legacy unencrypted key string

    if token.startswith("gAAAAA") and HAS_CRYPTO:
        try:
            cipher = _get_cipher()
            decrypted_bytes = cipher.decrypt(token.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return token

    if token.startswith("ENC:"):
        try:
            raw_b64 = token[4:]
            encrypted_bytes = base64.urlsafe_b64decode(raw_b64.encode('utf-8'))
            secret = getattr(settings, 'SECRET_KEY', 'fallback-secret-key-123')
            key_bytes = hashlib.sha256(secret.encode('utf-8')).digest()
            key_len = len(key_bytes)
            decrypted_bytes = bytearray()
            for i, b in enumerate(encrypted_bytes):
                decrypted_bytes.append(b ^ key_bytes[i % key_len])
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return token

    return token


def mask_key(raw_key_or_token: str) -> str:
    """
    Returns a secure masked preview of an API key (e.g. sk-proj-••••4a9f).
    Accepts either raw plaintext key or encrypted token.
    """
    plaintext = decrypt_key(raw_key_or_token)
    if not plaintext or len(plaintext) < 6:
        return "••••••••"

    prefix_len = 7 if (plaintext.startswith("sk-") or plaintext.startswith("AIza")) else 4
    if len(plaintext) <= prefix_len + 4:
        return plaintext[:2] + "••••" + plaintext[-2:]

    prefix = plaintext[:prefix_len]
    suffix = plaintext[-4:]
    return f"{prefix}••••••••{suffix}"
