"""Test script to control illumination from a MQTT topic."""

import asyncio
import logging
import logging.config
import os

from intervention_system.deploy import client_config_sample_cloudmqtt_path
from intervention_system.illumination.mqtt_client import Illuminator, topics
from intervention_system.mqtt_clients import message_string_encoding
from intervention_system.protocol import illumination_topic, deployment_topic
from intervention_system.util import config
from intervention_system.util.async import (
    register_keyboard_interrupt_signals, run_function
)
from intervention_system.util.logging import logging_config

# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


class MockIlluminator(Illuminator):
    """Sets NeoPixel illumination based on messages from the broker."""

    def init_illumination(self):
        """Initialize illumination support."""
        pass

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

    def set_illumination(self, illumination_params):
        """Set the lights to some illumination."""
        logger.info('Mock setting lights to: {}'.format(illumination_params))


if __name__ == '__main__':
    register_keyboard_interrupt_signals()

    # Load configuration
    config_path = client_config_sample_cloudmqtt_path
    configuration = config.config_load(config_path, keyfile_path=None)

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = MockIlluminator(loop, **configuration['broker'], topics=topics)
    run_function(mqttc.run)
    logger.info('Finished!')
