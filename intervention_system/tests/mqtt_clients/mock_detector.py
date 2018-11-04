"""Test script to send control messages to a MQTT topic."""

import argparse
import asyncio
import logging
import logging.config
import os
import random

from intervention_system.deploy import (
    client_config_sample_cloudmqtt_name, client_configs_sample_path
)
from intervention_system.mqtt_clients import AsyncioClient
from intervention_system.protocol import illumination_topic
from intervention_system.util import config
from intervention_system.util.async import (
    register_keyboard_interrupt_signals, run_function
)
from intervention_system.util.logging import logging_config

# Program parameters
switch_interval = 4
illumination_messages = [
    '{"mode": "clear"}',
    '{"mode": "breathe", "intensity": 255, "wait_ms": 2}',
    ('{"mode": "wipe", "colors": '
     '[{"red": 0, "green": 0, "blue": 255, "wait_ms": 40, "hold_ms": 0}, '
     '{"red": 0, "green": 0, "blue": 0, "wait_ms": 40, "hold_ms": 0}], '
     '"loop": true}'),
    '{"mode": "theater", "color": {"red": 255, "green": 255, "blue": 255}, "wait_ms": 200}',
    '{"mode": "rainbow", "wait_ms": 2}'
]


# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


class MockDetector(AsyncioClient):
    """Sends messages to broker based on operator actions."""

    def on_connect(self, client, userdata, flags, rc):
        """When the client connects, handle it."""
        super().on_connect(client, userdata, flags, rc)
        self.client.publish('connect', 'detection client', qos=2)

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        illumination_message = random.choice(illumination_messages)
        logger.info('Sending illumination message: {}'.format(illumination_message))
        self.client.publish(illumination_topic, illumination_message, qos=2)
        await asyncio.sleep(switch_interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Receive illumination system messages.')
    parser.add_argument(
        '--config', '-c', type=str, default=client_config_sample_cloudmqtt_name,
        help=(
            'Name of client settings file in {}. Default: {}'
            .format(client_configs_sample_path, client_config_sample_cloudmqtt_name)
        )
    )
    args = parser.parse_args()
    config_name = args.config
    register_keyboard_interrupt_signals()

    # Load configuration
    config_path = os.path.join(client_configs_sample_path, config_name)
    configuration = config.config_load(config_path, keyfile_path=None)

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = MockDetector(loop, **configuration['broker'])
    run_function(mqttc.run)
    logger.info('Finished!')
