"""Test script to send a hello world message to a test MQTT topic."""

import asyncio
import logging
import logging.config

from picamera_mqtt.deploy import client_config_sample_cloudmqtt_path
from picamera_mqtt.mqtt_clients import AsyncioClient, message_string_encoding
from picamera_mqtt.util import config
from picamera_mqtt.util.async import (
    register_keyboard_interrupt_signals, run_function
)
from picamera_mqtt.util.logging import logging_config

# Program parameters
topic = 'testing-publish'
message = 'hello, world!'
publish_interval = 4
publish_qos = 2
receive_qos = 2

# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


class Publisher(AsyncioClient):
    """Publishes a message to the broker."""

    def on_topic(self, client, userdata, msg):
        """Handle any messages from the broker on the preset topic."""
        logger.info('Received message on subscribed topic: {}'.format(
            msg.payload.decode(message_string_encoding))
        )

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        self.client.message_callback_add(topic, self.on_topic)

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        logger.info('Publishing message: {}'.format(message))
        self.publish_message(topic, message, publish_qos)
        await asyncio.sleep(publish_interval)


if __name__ == '__main__':
    register_keyboard_interrupt_signals()

    # Load configuration
    config_path = client_config_sample_cloudmqtt_path
    configuration = config.config_load(config_path)

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = Publisher(
        loop, **configuration['broker'], topics={topic: receive_qos}
    )
    run_function(mqttc.run)
    logger.info('Finished!')
