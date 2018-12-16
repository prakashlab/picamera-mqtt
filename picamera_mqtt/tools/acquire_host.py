"""Test script to obtain a single image snapshot with remote cameras."""

import argparse
import asyncio
import logging
import logging.config

from picamera_mqtt import data_path
from picamera_mqtt.deploy import (
    client_config_plain_name, client_configs_path
)
from picamera_mqtt.imaging.mqtt_client_host import Host, topics
from picamera_mqtt.util import config
from picamera_mqtt.util.async import (
    register_keyboard_interrupt_signals, run_function
)
from picamera_mqtt.util.logging import logging_config


# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


# Program parameters
final_image_receive_timeout = 10


class AcquireHost(Host):
    """Acquires remote images in a single time point."""

    def __init__(self, *args, capture_name='acquire', **kwargs):
        super().__init__(*args, **kwargs)
        self.capture_name = capture_name

    def build_capture_filename(self, capture):
        return '{} {} {}'.format(
            self.capture_name,
            capture['metadata']['client_name'],
            capture['metadata']['capture_time']['datetime']
        )

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        for target_name in self.target_names:
            self.request_image(target_name, extra_metadata={
                'host': 'acquire_host'
            })
        logger.info(
            'Requested images. Quitting in {} seconds...'
            .format(final_image_receive_timeout)
        )
        await asyncio.sleep(final_image_receive_timeout)
        raise asyncio.CancelledError


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Acquire a snapshot of images at a single time point.'
    )
    config.add_config_arguments(
        parser, client_configs_path, client_config_plain_name
    )
    parser.add_argument(
        '--output_dir', '-o', type=str, default=data_path,
        help=(
            'Directory to save captured images and metadata. '
            'Default: {}'.format(data_path)
        )
    )
    parser.add_argument(
        '--output_prefix', '-p', type=str, default='acquire',
        help=(
            'Filename prefix of captured image and metadata files. '
            'Default: {}'.format('acquire')
        )
    )
    args = parser.parse_args()
    capture_dir = args.output_dir
    capture_name = args.output_prefix
    configuration = config.load_config_from_args(args)

    register_keyboard_interrupt_signals()

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = AcquireHost(
        loop, **configuration['broker'], **configuration['host'],
        topics=topics, capture_dir=capture_dir, capture_name=capture_name
    )
    run_function(mqttc.run)
