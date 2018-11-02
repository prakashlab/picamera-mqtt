"""Generate a random key."""
import argparse
import os

from intervention_client import config
from intervention_client import files

repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_path = os.path.dirname(repo_path)
default_keyfile_path = os.path.join(project_path, 'settings.key')


def main(key_path):
    key = config.generate_key()
    files.save_bytestring(key, key_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a key file.')
    parser.add_argument(
        '-k', '--key', type=str, default=default_keyfile_path,
        help='Path to save the key.'
    )

    args = parser.parse_args()
    main(args.key)
