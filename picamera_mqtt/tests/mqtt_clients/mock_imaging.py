"""Test script to control illumination from a MQTT topic."""

import argparse
import asyncio
import logging
import logging.config
import os

from picamera_mqtt.deploy import (
    client_config_sample_localhost_name, client_configs_sample_path
)
from picamera_mqtt.imaging import imaging
from picamera_mqtt.imaging.mqtt_client_camera import Imager, topics
from picamera_mqtt.mqtt_clients import message_string_encoding
from picamera_mqtt.util import config
from picamera_mqtt.util.async import (
    register_keyboard_interrupt_signals, run_function
)
from picamera_mqtt.util.logging import logging_config

# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


class MockImager(Imager):
    """Generates random images based on messages from the broker."""

    def init_imaging(self):
        """Initialize imaging support."""
        self.camera = imaging.MockCamera()
        if self.client_name in self.camera_params:
            self.camera.set_params(**self.camera_params[self.client_name])

    def on_deployment_topic(self, client, userdata, msg):
        """Handle any device deployment messages."""
        command = msg.payload.decode(message_string_encoding)
        if command == 'reboot':
            logger.info('Mock rebooting (nop)...')
        elif command == 'shutdown':
            logger.info('Mock shutting down (nop)...')
        elif command == 'restart':
            logger.info('Mock restarting (nop)...')
        elif command == 'git pull':
            logger.info('Mock updating local repo (nop)...')
        elif command == 'stop':
            logger.info('Stopping...')
            raise KeyboardInterrupt

    async def attempt_reconnect(self):
        """Prepare the system for a reconnection attempt."""
        logger.info('Mock reconnecting (nop)...')
        await asyncio.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate random images on request.'
    )
    config.add_config_arguments(
        parser,
        client_configs_sample_path, client_config_sample_localhost_name
    )
    args = parser.parse_args()
    configuration = config.load_config_from_args(args)

    register_keyboard_interrupt_signals()

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = MockImager(
        loop, **configuration['broker'], **configuration['deploy'],
        topics=topics, camera_params=configuration['targets']
    )
    run_function(mqttc.run)
    logger.info('Finished!')
