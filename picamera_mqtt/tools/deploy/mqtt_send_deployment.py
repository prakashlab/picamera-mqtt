"""Send a MQTT message on the deployment topic."""

import argparse
import asyncio
import logging
import logging.config
import os

from intervention_system.deploy import (
    client_config_sample_cloudmqtt_name, client_configs_sample_path
)
from intervention_system.mqtt_clients import AsyncioClient
from intervention_system.protocol import deployment_topic
from intervention_system.util import config
from intervention_system.util.async import (
    register_keyboard_interrupt_signals, run_function
)
from intervention_system.util.logging import logging_config

# Program parameters
publish_qos = 2

# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


class Publisher(AsyncioClient):
    """Publishes a message to the broker."""

    def __init__(self, loop, message, **kwargs):
        """Save the message to send."""
        super().__init__(loop, **kwargs)
        self.message = message
        self.message_mid = None

    def on_publish(self, client, userdata, mid):
        """When the client publishes a message, handle it."""
        if mid == self.message_mid:
            logger.debug('Message {} published to broker'.format(message))
            raise KeyboardInterrupt

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        if self.message_mid is None:
            logger.info('Publishing message: {}'.format(self.message))
            message = self.publish_message(deployment_topic, self.message, publish_qos)
            self.message_mid = message.mid
        else:
            await asyncio.sleep(0.5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send a deployment message.')
    parser.add_argument('message', type=str, help='Message to send on the deployment topic.')
    parser.add_argument(
        '--config', '-c', type=str, default=client_config_sample_cloudmqtt_name,
        help=(
            'Name of client settings file in {}. Default: {}'
            .format(client_configs_sample_path, client_config_sample_cloudmqtt_name)
        )
    )
    args = parser.parse_args()
    config_name = args.config
    message = args.message
    register_keyboard_interrupt_signals()

    # Load configuration
    config_path = os.path.join(client_configs_sample_path, config_name)
    configuration = config.config_load(config_path, keyfile_path=None)

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = Publisher(
        loop, message, **configuration['broker']
    )
    run_function(mqttc.run)
