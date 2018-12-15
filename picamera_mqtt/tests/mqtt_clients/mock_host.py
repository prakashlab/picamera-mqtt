"""Test script to send control messages to a MQTT topic."""

import argparse
import asyncio
import datetime
import json
import logging
import logging.config
import os
import time

from picamera_mqtt.deploy import (
    client_config_sample_localhost_name, client_configs_sample_path
)
from picamera_mqtt.mqtt_clients import AsyncioClient, message_string_encoding
from picamera_mqtt.protocol import (
    connect_topic, control_topic, deployment_topic, imaging_topic
)
from picamera_mqtt.util import config, files
from picamera_mqtt.util.async import (
    register_keyboard_interrupt_signals, run_function
)
from picamera_mqtt.util.logging import logging_config

# Program parameters
acquisition_interval = 8


# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)
payload_log_max_len = 400

# Configure messaging
topics = {
    control_topic: {
        'qos': 2,
        'local_namespace': True,
        'subscribe': False,
        'log': False
    },
    imaging_topic: {
        'qos': 2,
        'local_namespace': True,
        'subscribe': True,
        'log': False
    },
    deployment_topic: {
        'qos': 2,
        'local_namespace': True,
        'subscribe': True,
        'log': True
    },
    connect_topic: {
        'qos': 2,
        'local_namespace': False,
        'subscribe': True,
        'log': True
    }
}


class MockHost(AsyncioClient):
    """Sends messages to broker based on operator actions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_id = 1

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        self.client.message_callback_add(
            self.get_topic_path(imaging_topic), self.on_imaging_topic
        )

    def on_imaging_topic(self, client, userdata, msg):
        payload = msg.payload.decode(message_string_encoding)
        try:
            capture = json.loads(payload)
        except json.JSONDecodeError:
            payload_truncated = payload[:400] + (payload[400:] and '...')
            logger.error('Malformed image: {}'.format(payload_truncated))
            return
        file_name = '{} {} {}'.format(
            capture['metadata']['client_name'],
            capture['metadata']['image_id'],
            capture['capture_time']['datetime']
        )
        image_base64 = capture.pop('image', None)
        files.b64_string_bytes_save(image_base64, '{}.jpg'.format(file_name))
        capture['image'] = '{}.jpg'.format(file_name)
        files.json_dump(capture, '{}.json'.format(file_name))
        capture['camera_params'] = '...'
        logger.info('Received image on topic {}: {}'.format(
            msg.topic, json.dumps(capture)
        ))

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        acquisition_message = json.dumps({
            'action': 'acquire_image',
            'command_time': {
                'time': time.time(),
                'datetime': str(datetime.datetime.now())
            },
            'metadata': {
                'client_name': self.target_name,
                'image_id': self.image_id
            }
        })
        self.image_id += 1
        logger.info(
            'Sending acquisition message to topic {}: {}'.format(
                self.get_topic_path(control_topic), acquisition_message
            )
        )
        self.publish_message(control_topic, acquisition_message)
        await asyncio.sleep(acquisition_interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Send image acquisition messages and save acquired images.'
    )
    parser.add_argument(
        '--config', '-c', type=str,
        default=client_config_sample_localhost_name,
        help=('Name of client settings file in {}. Default: {}'.format(
            client_configs_sample_path, client_config_sample_localhost_name
        ))
    )
    args = parser.parse_args()
    config_name = args.config
    register_keyboard_interrupt_signals()

    # Load configuration
    config_path = os.path.join(client_configs_sample_path, config_name)
    configuration = config.config_load(config_path)

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = MockHost(
        loop, **configuration['broker'], **configuration['host'],
        topics=topics
    )
    run_function(mqttc.run)
    logger.info('Finished!')
