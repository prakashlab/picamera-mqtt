"""Support for reading and writing files."""
import base64
import json
import pathlib

# Directory I/O

def ensure_path(path):
    """Ensure the existence of the path by making directories as needed."""
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


# JSON I/O

def json_dump(obj, path):
    """Save a json object to a file."""
    with open(path, 'w') as f:
        return json.dump(obj, f, indent=2)

def json_load(path):
    """Load a json object from a file."""
    with open(path, 'r') as f:
        return json.load(f)

# String I/O

def string_save(string, path):
    """Save a string to a file."""
    with open(path, 'w') as f:
        f.write(string)

def string_load(path):
    """Load a string from a file."""
    with open(path, 'r') as f:
        return f.read()

# Bytes I/O

def bytes_save(bytes_data, path):
    """Save bytes to a file."""
    with open(path, 'wb') as f:
        f.write(bytes_data)

def bytes_load(path):
    """Load bytest from a file."""
    with open(path, 'rb') as f:
        return f.read()

# Bytestring Base64 I/O

def bytes_b64_save(bytes_data, path, char_encoding='utf-8'):
    """Save bytes as a Base64 string to a file."""
    b64_data = base64.b64encode(bytes_data)
    b64_string = b64_data.decode(char_encoding)
    string_save(b64_string, path)

def bytes_b64_load(path, char_encoding='utf-8'):
    """Load bytes as a Base64 string from a file."""
    b64_string = string_load(path)
    b64_data = bytes(b64_string, char_encoding)
    return base64.b64decode(b64_data)

def b64_string_bytes_save(b64_string, path, char_encoding='utf-8'):
    b64_data = bytes(b64_string, char_encoding)
    bytes_data = base64.b64decode(b64_data)
    bytes_save(bytes_data, path)
