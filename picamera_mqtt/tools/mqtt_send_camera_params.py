"""Send an imaging control message to adjust camera params."""

import argparse
import asyncio
import logging
import logging.config

from picamera_mqtt.deploy import (
    client_config_sample_localhost_name, client_configs_sample_path
)
from picamera_mqtt.imaging import imaging
from picamera_mqtt.imaging.mqtt_client_host import Host
from picamera_mqtt.mqtt_clients import message_string_encoding
from picamera_mqtt.protocol import control_topic, params_topic
from picamera_mqtt.util import config
from picamera_mqtt.util.async import (
    register_keyboard_interrupt_signals, run_function
)
from picamera_mqtt.util.logging import logging_config

# Set up logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Configure messaging
topics = {
    control_topic: {
        'qos': 2,
        'local_namespace': True,
        'subscribe': False,
        'log': False
    },
    params_topic: {
        'qos': 2,
        'local_namespace': True,
        'subscribe': True,
        'log': True
    }
}


class Publisher(Host):
    """Send camera params to the camera client."""

    def __init__(self, loop, camera_params, **kwargs):
        super().__init__(loop, **kwargs)
        self.message_mid = None
        self.camera_params = camera_params

    def on_params_topic(self, client, userdata, msg):
        payload = msg.payload.decode(message_string_encoding)
        logger.info('Received camera params response: {}'.format(payload))
        raise KeyboardInterrupt

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        if self.message_mid is None:
            logger.info('Sending camera params: {}'.format(self.camera_params))
            message = self.set_params(
                self.target_names[0], **self.camera_params
            )[0]
            self.message_mid = message.mid
        else:
            await asyncio.sleep(0.5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send params to a camera.')
    config.add_config_arguments(
        parser,
        client_configs_sample_path, client_config_sample_localhost_name
    )
    parser.add_argument(
        '--target_name', '-t', type=str, default='camera_1',
        help=('Name of camera client to send the params to. Default: camera_1')
    )
    imaging.add_camera_params_arguments(parser)
    args = parser.parse_args()
    configuration = config.load_config_from_args(args)
    camera_params = imaging.parse_camera_params_from_args(args)

    register_keyboard_interrupt_signals()

    # Override configuration
    configuration['host']['client_name'] = 'mqtt_send_camera_params'
    configuration['host']['target_names'] = [args.target_name]

    logger.info('Starting client...')
    loop = asyncio.get_event_loop()
    mqttc = Publisher(
        loop, camera_params,
        **configuration['broker'], **configuration['host'],
        topics=topics
    )
    run_function(mqttc.run)
