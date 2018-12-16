"""Test script to obtain timelapses with remote cameras."""

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
final_image_receive_timeout = 5


class TimelapseHost(Host):
    """Acquires remote images for a timelapse."""

    def __init__(
        self, *args, acquisition_interval=15, acquisition_length=5, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.acquisition_interval = acquisition_interval
        self.acquisition_length = acquisition_length

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        requested_image = False
        for target_name in self.target_names:
            if self.image_ids[target_name] <= self.acquisition_length:
                self.request_image(target_name, extra_metadata={
                    'host': 'timelapse_host'
                })
                requested_image = True
        await asyncio.sleep(self.acquisition_interval)
        if not requested_image:
            logger.info(
                'No more images to request. Quitting in {} seconds...'
                .format(final_image_receive_timeout)
            )
            await asyncio.sleep(final_image_receive_timeout)
            raise asyncio.CancelledError


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Acquire timelapse series.'
    )
    config.add_config_arguments(
        parser, client_configs_path, client_config_plain_name
    )
    parser.add_argument(
        '--interval', '-i', type=int, default=15,
        help='Image acquisition interval in seconds. Default: 15'
    )
    parser.add_argument(
        '--number', '-n', type=int, default=5,
        help='Number of images to acquire. Default: 5'
    )
    parser.add_argument(
        '--output_dir', '-o', type=str, default=data_path,
        help=(
            'Directory to save captured images and metadata. '
            'Default: {}'.format(data_path)
        )
    )
    args = parser.parse_args()
    acquisition_interval = args.interval
    acquisition_length = args.number
    capture_dir = args.output_dir
    configuration = config.load_config_from_args(args)

    register_keyboard_interrupt_signals()

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = TimelapseHost(
        loop, **configuration['broker'], **configuration['host'],
        topics=topics, capture_dir=capture_dir,
        acquisition_interval=acquisition_interval,
        acquisition_length=acquisition_length,
    )
    run_function(mqttc.run)
    logger.info('Finished!')
