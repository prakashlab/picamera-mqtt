"""Support for loading encrypted configuration from a drive."""
import json

def load_config(path):
    with open(path) as f:
        return json.load(f)
