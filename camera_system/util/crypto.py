"""Support for data encryption."""
import json

import nacl.utils
from nacl.encoding import Base64Encoder
from nacl.secret import SecretBox

from intervention_system.util import files

# SecretBox Management

def generate_box(key=None):
    """Generate a SecretBox with an encryption key.
    
    Generates a random key if no key is provided.
    """
    if key is None:
        key = nacl.utils.random(SecretBox.KEY_SIZE)
    return SecretBox(key)

def save_box(box, path):
    """Save a SecretBox to file."""
    key = bytes(box)
    files.bytes_b64_save(key, path)

def load_box(path):
    """Load a SecretBox from file."""
    key = files.bytes_b64_load(path)
    return SecretBox(key)

# String Encryption

def string_encrypt(
    string_plain, box, encoder=Base64Encoder, char_encoding='utf-8'
):
    """Encrypt a string and encode it as a string."""
    bytes_plain = string_plain.encode(char_encoding)
    return box.encrypt(bytes_plain, encoder=encoder).decode(char_encoding)

def string_decrypt(
    string_cipher, box, encoder=Base64Encoder, char_encoding='utf-8'
):
    """Decrypt a string after decoding it as a string."""
    bytes_cipher = bytes(string_cipher, char_encoding)
    bytes_plain = box.decrypt(bytes_cipher, encoder=encoder)
    return bytes_plain.decode(char_encoding)

# String I/O

def string_secret_save(string_plain, path, box):
    """Encrypt a string, base64 encode it, and save it to a file."""
    string_cipher = string_encrypt(string_plain, box, encoder=Base64Encoder)
    files.string_save(string_cipher)

def string_secret_load(path, box):
    """Load a string from file, base64 decode it, and decrypt it."""
    string_cipher = files.string_load(path)
    return string_decrypt(string_cipher, box, encoder=Base64Encoder)

# JSON Encryption

def json_secret_dumps(obj, box):
    """Encrypt json obj and base64 encode it."""
    string_plain = json.dumps(obj)
    return string_encrypt(string_plain, box, encoder=Base64Encoder)

def json_secret_loads(string_cipher, box):
    """Base64 decode and decrypt json data."""
    string_plain = string_decrypt(string_cipher, box, encoder=Base64Encoder)
    return json.loads(string_plain)

# JSON I/O

def json_secret_dump(obj, box, path):
    """Encrypt json data, base64 encode it, and save it to a file."""
    string_cipher = json_secret_dumps(obj, box)
    files.string_save(string_cipher, path)

def json_secret_load(path, box):
    """Load json data from file, base64 decode it, and decrypt it."""
    string_cipher = files.string_load(path)
    return json_secret_loads(string_cipher, box)
