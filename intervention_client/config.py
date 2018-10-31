"""Support for loading encrypted configuration from a drive."""
import nacl.secret
import nacl.utils

from intervention_client import files

def generate_key():
    """Generate a random encryption key for a SecretBox."""
    return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

def encrypt_config(config, keyfile_path):
    """Encrypt the values of a config."""
    box = nacl.secret.SecretBox(files.load_bytestring(keyfile_path))
    return {
        key: list(box.encrypt(value.encode('utf-8')))
        for (key, value) in config.items()
    }

def decrypt_config(config, keyfile_path):
    """Decrypt the values of a config."""
    box = nacl.secret.SecretBox(files.load_bytestring(keyfile_path))
    return {
        key: box.decrypt(bytes(value)).decode('utf-8')
        for (key, value) in config.items()
    }

def load_config(config_path, keyfile_path=None):
    """Load a json config from the provided path."""
    encrypted_config = files.load_json(config_path)
    if keyfile_path is None:
        return encrypted_config  # Assume the config is in plaintext
    else:
        return decrypt_config(encrypted_config, keyfile_path)
