"""Encrypt a settings JSON file."""
import argparse
import os

from intervention_system import repo_path
from intervention_system.util import config

project_path = os.path.dirname(repo_path)
default_keyfile_path = os.path.join(project_path, 'settings.key')
default_input_path = '/media/usb0/settings.json'
default_output_path = '/media/usb0/settings_encrypted.json'


def main(input_path, key_path, output_path):
    config_plain = config.config_load(input_path, None)
    config.config_dump(config_plain, output_path, key_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Encrypt a settings file.')
    parser.add_argument(
        '-i', '--input', type=str, default=default_input_path,
        help='Path of the file to encrypt. Default: {}'.format(default_input_path)
    )
    parser.add_argument(
        '-k', '--key', type=str, default=default_keyfile_path,
        help='Path to the key file. Default: {}'.format(default_keyfile_path)
    )
    parser.add_argument(
        '-o', '--output', type=str, default=default_output_path,
        help='Path to save the encrypted file. Default: {}'.format(default_output_path)
    )

    args = parser.parse_args()
    main(args.input, args.key, args.output)
