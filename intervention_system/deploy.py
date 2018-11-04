"""Shared parameters for deployment."""

import os

from intervention_system import deploy_path

keys_path = deploy_path
settings_key_path = os.path.join(keys_path, 'settings.key')
client_configs_path = '/media/usb0/'
client_config_plain_name = 'settings.json'
client_config_cipher_name = 'settings_encrypted.json'
client_config_plain_path = os.path.join(client_configs_path, client_config_plain_name)
client_config_cipher_path = os.path.join(client_configs_path, client_config_cipher_name)
