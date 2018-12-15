"""Support for loading json configurations from a drive."""
from picamera_mqtt.util import files

def config_dump(config_obj, config_path):
    """Dump and encrypt a json config to a file."""
    files.json_dump(config_obj, config_path)

def config_load(config_path):
    """Load a json config from a file."""
    return files.json_load(config_path)
