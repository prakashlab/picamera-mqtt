"""Decrypt the keys of a settings JSON file."""
import argparse
import os

from intervention_system.deploy import settings_key_path as default_keyfile_path
from intervention_system.deploy import client_config_cipher_path as default_input_path
from intervention_system.deploy import client_configs_path
from intervention_system.util import config
from intervention_system.tools.config.encrypt_config import default_output_path as default_input_path

default_output_path = os.path.join(client_configs_path, 'settings_decrypted.json')

def main(input_path, key_path, output_path):
    config_plain = config.config_load(input_path, key_path)
    config.config_dump(config_plain, output_path, None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decrypt a settings file.')
    parser.add_argument(
        '-i', '--input', type=str, default=default_input_path,
        help='Path of the file to decrypt. Default: {}'.format(default_input_path)
    )
    parser.add_argument(
        '-k', '--key', type=str, default=default_keyfile_path,
        help='Path to the key file. Default: {}'.format(default_keyfile_path)
    )
    parser.add_argument(
        '-o', '--output', type=str, default=default_output_path,
        help='Path to save the decrypted file. Default: {}'.format(default_output_path)
    )

    args = parser.parse_args()
    main(args.input, args.key, args.output)
