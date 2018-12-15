"""Test script to send control messages to a MQTT topic."""

import datetime
import json
import logging
import logging.config
import time

from picamera_mqtt.mqtt_clients import AsyncioClient, message_string_encoding
from picamera_mqtt.protocol import (
    connect_topic, control_topic, deployment_topic, imaging_topic
)
from picamera_mqtt.util import files


# Set up logging
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


class Host(AsyncioClient):
    """Sends imaging control messages to broker and saves received images."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_ids = {
            target_name: 1 for target_name in self.target_names
        }

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        for topic_path in self.get_topic_paths(imaging_topic):
            self.client.message_callback_add(topic_path, self.on_imaging_topic)

    def on_imaging_topic(self, client, userdata, msg):
        payload = msg.payload.decode(message_string_encoding)
        receive_time = time.time()
        receive_datetime = str(datetime.datetime.now())
        try:
            capture = json.loads(payload)
        except json.JSONDecodeError:
            payload_truncated = (
                payload[:payload_log_max_len]
                + (payload[payload_log_max_len:] and '...')
            )
            logger.error('Malformed image: {}'.format(payload_truncated))
            return
        capture['metadata']['receive_time'] = {
            'time': receive_time,
            'datetime': receive_datetime
        }

        self.save_captured_image(capture)
        capture.pop('image', None)
        self.save_captured_metadata(capture)
        capture['camera_params'] = '...'
        logger.info('Received image on topic {}: {}'.format(
            msg.topic, json.dumps(capture)
        ))

    def build_capture_filename(self, capture):
        return '{} {} {}'.format(
            capture['metadata']['client_name'],
            capture['metadata']['image_id'],
            capture['metadata']['capture_time']['datetime']
        )

    def save_captured_image(self, capture):
        capture_filename = self.build_capture_filename(capture)
        image_filename = '{}.{}'.format(capture_filename, capture['format'])
        image_base64 = capture['image']
        files.b64_string_bytes_save(image_base64, image_filename)

    def save_captured_metadata(self, capture):
        capture_filename = self.build_capture_filename(capture)
        image_filename = '{}.{}'.format(capture_filename, capture['format'])
        capture['image'] = image_filename
        files.json_dump(capture, '{}.json'.format(capture_filename))

    def request_image(
        self, target_name, format='jpeg',
        capture_format_params={'quality': 100},
        transport_format_params={'quality': 80},
        extra_metadata={}
    ):
        if target_name not in self.target_names:
            logger.error(
                'Unknown camera client target: {}'.format(target_name)
            )
            return

        acquisition_obj = {
            'action': 'acquire_image',
            'format': format,
            'capture_format_params': capture_format_params,
            'transport_format_params': transport_format_params,
            'metadata': {
                'client_name': target_name,
                'image_id': self.image_ids[target_name],
                'command_time': {
                    'time': time.time(),
                    'datetime': str(datetime.datetime.now())
                },
            }
        }
        for (key, value) in extra_metadata.items():
            acquisition_obj['metadata'][key] = value
        acquisition_message = json.dumps(acquisition_obj)
        self.image_ids[target_name] += 1
        logger.info(
            'Sending acquisition message to topic {}: {}'.format(
                self.get_topic_paths(
                    control_topic, local_namespace=target_name
                )[0], acquisition_message
            )
        )
        self.publish_message(
            control_topic, acquisition_message, local_namespace=target_name
        )
