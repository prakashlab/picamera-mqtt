"""Test script to send control messages to a MQTT topic."""

import asyncio
import contextlib
import logging
import logging.config
import os
import random

from intervention_client import config
from intervention_client.mqtt import AsyncioClient
from intervention_client.mqtt_illumination import repo_path

# Program parameters
illumination_topic = 'illumination'
message_encoding = 'utf-8'
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
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'f': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'h': {
            'class': 'logging.StreamHandler',
            'formatter': 'f',
            'level': logging.INFO
        }
    },
    'root': {
        'handlers': ['h'],
        'level': logging.INFO
    }
}
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


class MockDetector(AsyncioClient):
    """Sends messages to broker based on operator actions."""

    def on_connect(self, client, userdata, flags, rc):
        """When the client connects, handle it."""
        super().on_connect(client, userdata, flags, rc)
        self.client.publish('connect', 'detection client', qos=2)

    async def attempt_reconnect(self):
        """Prepare the system for a reconnection attempt."""
        pass

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        illumination_message = random.choice(illumination_messages)
        logger.info('Sending illumination message: {}'.format(illumination_message))
        self.client.publish(illumination_topic, illumination_message, qos=2)
        await asyncio.sleep(switch_interval)


if __name__ == '__main__':
    # Config file paths
    config_path = os.path.join(repo_path, 'config', 'settings.json')

    # Load configuration
    configuration = config.load_config(config_path, keyfile_path=None)
    hostname = configuration['hostname']
    port = int(configuration['port'])
    username = configuration['username']
    password = configuration['password']
    ca_certs = '/etc/ssl/certs/ca-certificates.crt'

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = MockDetector(
        loop, hostname, port,
        username=username, password=password, ca_certs=ca_certs
    )
    task = loop.create_task(mqttc.run())
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        logger.info('Quitting...')
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            loop.run_until_complete(asyncio.gather(*pending))
    finally:
        loop.close()
    logger.info('Finished!')
