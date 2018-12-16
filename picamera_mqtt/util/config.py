"""Support for loading json configurations from a drive."""
import logging
import os

from picamera_mqtt.util import files


# Set up logging
logger = logging.getLogger(__name__)


# Config load/save

def config_dump(config_obj, config_path):
    """Dump and encrypt a json config to a file."""
    files.json_dump(config_obj, config_path)

def config_load(config_path):
    """Load a json config from a file."""
    return files.json_load(config_path)


# Command-line args

def add_config_arguments(arg_parser, default_config_path, default_config_name):
    arg_parser.add_argument(
        '--config_dir', '-d', type=str, default=default_config_path,
        help=(
            'Directory containing the client settings file. Default: {}'
            .format(default_config_path)
        )
    )
    arg_parser.add_argument(
        '--config', '-c', type=str, default=default_config_name,
        help=('Name of client settings file in config_dir. Default: {}'.format(
            default_config_name
        ))
    )

def load_config_from_args(parsed_args):
    config_dir = parsed_args.config_dir
    config_name = parsed_args.config
    config_path = os.path.join(config_dir, config_name)
    logger.info('Loading configuration from {}...'.format(config_path))
    configuration = config_load(config_path)
    return configuration
