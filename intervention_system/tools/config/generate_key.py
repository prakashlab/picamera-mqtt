"""Generate a random key."""
import argparse
import os

from intervention_system.deploy import settings_key_path as default_keyfile_path
from intervention_system.util import crypto


def main(key_path):
    box = crypto.generate_box()
    crypto.save_box(box, key_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a key file.')
    parser.add_argument(
        '-k', '--key', type=str, default=default_keyfile_path,
        help='Path to save the key. Default: {}'.format(default_keyfile_path)
    )

    args = parser.parse_args()
    main(args.key)
