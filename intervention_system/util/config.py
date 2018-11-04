"""Support for loading json configurations from a drive."""
from intervention_system.util import crypto, files

def config_encrypt(config_obj, keyfile_path):
    """JSON dump and encrypt a config object to a string."""
    box = crypto.load_box(keyfile_path)
    return crypto.json_secret_dumps(config_obj, box)

def config_decrypt(string_cipher, keyfile_path):
    """Decrypt and JSON load a config object from a string."""
    box = crypto.load_box(keyfile_path)
    return crypto.json_secret_loads(string_cipher, box)

def config_dump(config_obj, config_path, keyfile_path):
    """Dump and encrypt a json config to a file."""
    if keyfile_path is None:
        files.json_dump(config_obj, config_path)
    else:
        box = crypto.load_box(keyfile_path)
        crypto.json_secret_dump(config_obj, box, config_path)

def config_load(config_path, keyfile_path):
    """Load a json config from a file."""
    if keyfile_path is None:
        return files.json_load(config_path)
    else:
        box = crypto.load_box(keyfile_path)
        return crypto.json_secret_load(config_path, box)
