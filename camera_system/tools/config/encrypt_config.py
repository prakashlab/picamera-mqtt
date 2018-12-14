"""Encrypt a settings JSON file."""
import argparse
import os

from intervention_system.deploy import settings_key_path as default_keyfile_path
from intervention_system.deploy import client_config_plain_path as default_input_path
from intervention_system.deploy import client_config_cipher_path as default_output_path
from intervention_system.util import config


def main(input_path, key_path, output_path):
    config_plain = config.config_load(input_path, None)
    try:
        config.config_dump(config_plain, output_path, key_path)
    except PermissionError:
        raise PermissionError(
            'Could not write to {}. Make sure the program '
            'is run with privileged permissions!'.format(output_path)
        )


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
