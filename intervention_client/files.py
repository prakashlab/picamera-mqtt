"""Support for reading and writing files."""
import json

def save_json(data, path):
    """Save a json to the provided path."""
    with open(path, 'w') as f:
        return json.dump(data, f)

def load_json(path):
    """Load a json from the provided path."""
    with open(path, 'r') as f:
        return json.load(f)

def save_bytestring(bytestring, path):
    """Save a string to a path."""
    with open(path, 'wb') as f:
        f.write(bytestring)

def load_bytestring(path):
    """Load a string from a path."""
    with open(path, 'rb') as f:
        return f.read()
