"""Decrypt the keys of a settings JSON file."""
import argparse
import os

from intervention_client import config
from intervention_client import files

repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_path = os.path.dirname(repo_path)
default_keyfile_path = os.path.join(project_path, 'settings.key')
default_input_path = '/media/usb0/settings_encrypted.json'
default_output_path = '/media/usb0/settings_decrypted.json'


def main(input_path, key_path, output_path):
    plain = config.load_config(input_path, keyfile_path=key_path)
    files.save_json(plain, output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decrypt a settings file.')
    parser.add_argument(
        '-i', '--input', type=str, default=default_input_path,
        help='Path of the file to decrypt.'
    )
    parser.add_argument(
        '-k', '--key', type=str, default=default_keyfile_path,
        help='Path to the key file.'
    )
    parser.add_argument(
        '-o', '--output', type=str, default=default_output_path,
        help='Path to save the decrypted file.'
    )

    args = parser.parse_args()
    main(args.input, args.key, args.output)
