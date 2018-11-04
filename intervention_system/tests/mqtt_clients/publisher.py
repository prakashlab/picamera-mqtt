"""Test script to send a hello world message to a test MQTT topic."""

import asyncio
import logging

from intervention_system.mqtt_clients import AsyncioClient, message_string_encoding
from intervention_system.util.async import run_function

# Program parameters
hostname = 'm15.cloudmqtt.com'
port = 16076
username = 'lpkbaxec'
password = 'limdi7J_A3Tc'
topic = 'testing-publish'
message = 'hello, world!'
publish_interval = 4
publish_qos = 2
receive_qos = 2

# Set up logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


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
    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = Publisher(
        loop, hostname, port,
        username=username, password=password, topics={topic: receive_qos}
    )
    run_function(mqttc.run)
    logger.info('Finished!')
