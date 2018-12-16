"""Test script to send control messages to a MQTT topic."""

import datetime
import json
import logging
import logging.config
import os
import time

from picamera_mqtt.mqtt_clients import AsyncioClient, message_string_encoding
from picamera_mqtt.protocol import (
    connect_topic, control_topic, deployment_topic, imaging_topic, params_topic
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
    params_topic: {
        'qos': 2,
        'local_namespace': True,
        'subscribe': True,
        'log': True
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

    def __init__(self, *args, capture_dir='', camera_params={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera_params = camera_params
        self.image_ids = {target_name: 1 for target_name in self.target_names}
        self.capture_dir = capture_dir

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        for topic_path in self.get_topic_paths(params_topic):
            self.client.message_callback_add(topic_path, self.on_params_topic)
        for topic_path in self.get_topic_paths(imaging_topic):
            self.client.message_callback_add(topic_path, self.on_imaging_topic)

    def on_params_topic(self, client, userdata, msg):
        payload = msg.payload.decode(message_string_encoding)
        target_name = msg.topic.split('/')[0]
        logger.info(
            'Received camera params response from target {}: {}'
            .format(target_name, payload)
        )

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
        logger.debug('Received image on topic {}: {}'.format(
            msg.topic, json.dumps(capture)
        ))

    def build_capture_filename(self, capture):
        return '{} {} {}'.format(
            capture['metadata']['client_name'],
            capture['metadata']['image_id'],
            capture['metadata']['capture_time']['datetime']
        )

    def save_captured_image(self, capture):
        files.ensure_path(self.capture_dir)
        capture_filename = self.build_capture_filename(capture)
        image_filename = '{}.{}'.format(capture_filename, capture['format'])
        image_base64 = capture['image']
        image_path = os.path.join(self.capture_dir, image_filename)
        files.b64_string_bytes_save(image_base64, image_path)
        logger.info('Saved image to: {}'.format(image_path))

    def save_captured_metadata(self, capture):
        files.ensure_path(self.capture_dir)
        capture_filename = self.build_capture_filename(capture)
        image_filename = '{}.{}'.format(capture_filename, capture['format'])
        capture['image'] = image_filename
        metadata_path = os.path.join(
            self.capture_dir, '{}.json'.format(capture_filename)
        )
        files.json_dump(capture, metadata_path)
        logger.info('Saved metadata to: {}'.format(metadata_path))

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
        return self.publish_message(
            control_topic, acquisition_message, local_namespace=target_name
        )

    def set_params(self, target_name, **params):
        update_obj = {'action': 'set_params'}
        for (key, value) in params.items():
            if value is not None:
                update_obj[key] = value
        logger.info('Setting {} camera parameters to: {}'.format(
            target_name, update_obj
        ))
        update_message = json.dumps(update_obj)
        return self.publish_message(
            control_topic, update_message, local_namespace=target_name
        )

    def set_params_from_stored(self, target_name):
        return self.set_params(target_name, **self.camera_params[target_name])

    def set_roi(self, target_name, zoom=None):
        self.set_params(target_name, roi_zoom=zoom)

    def set_shutter_speed(self, target_name, shutter_speed=None):
        self.set_params(target_name, shutter_speed=shutter_speed)

    def set_iso(self, target_name, iso=None):
        self.set_params(target_name, iso=iso)

    def set_resolution(self, target_name, width=None, height=None):
        self.set_params(
            target_name, resolution_width=width, resolution_height=height
        )

    def set_awb_gains(self, target_name, red=None, blue=None):
        self.set_params(target_name, awb_gain_red=red, awb_gain_blue=blue)
