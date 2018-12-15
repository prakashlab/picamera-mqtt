"""MQTT client support for remote control."""
import asyncio
import logging
import socket
import ssl

import paho.mqtt.client as mqtt

from picamera_mqtt.protocol import connect_topic, ping_topic

logger = logging.getLogger(__name__)

message_string_encoding = 'utf-8'


def build_topic_paths(namespaces, topic):
    return ['{}/{}'.format(namespace, topic) for namespace in namespaces]


class AsyncioHelper(object):
    """A helper to adapt the MQTT client to asyncio event loop."""

    def __init__(self, loop, client):
        """Add socket callbacks to the client."""
        self.loop = loop
        self.client = client
        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

    def on_socket_open(self, client, userdata, sock):
        """When the socket opens, add a reader callback to the loop."""
        logger.debug('Socket opened!')

        self.loop.add_reader(sock, client.loop_read)

    def on_socket_close(self, client, userdata, sock):
        """When the socket closes, remove the reader callback from the loop."""
        logger.debug('Socket closed!')
        self.loop.remove_reader(sock)

    def on_socket_register_write(self, client, userdata, sock):
        """When the writer is registered, add it to the loop."""
        logger.debug('Watching socket for writability...')

        self.loop.add_writer(sock, client.loop_write)

    def on_socket_unregister_write(self, client, userdata, sock):
        """When the writer is unregistered, remove it from the loop."""
        logger.debug('Stop watching socket for writability...')
        self.loop.remove_writer(sock)


class AsyncioClient(object):
    """Async MQTT client."""

    def __init__(
        self, loop,
        hostname='localhost', port=1883,
        username=None, password=None, client_id='',
        use_tls=False, ca_certs=None, tls_version=ssl.PROTOCOL_TLSv1_2,
        topics={},
        client_name='asyncio client', target_names=['asyncio client'],
        clean_session=True, ping_interval=2, ping_timeout=1
    ):
        """Initialize client state."""
        self.loop = loop
        self.client_id = client_id
        self.client_name = client_name
        self.target_names = target_names
        self.clean_session = clean_session
        self.client = mqtt.Client(
            client_id=client_id, clean_session=clean_session
        )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.enable_logger(logger=logger)
        self.helper = AsyncioHelper(self.loop, self.client)

        self.username = username
        self.password = password
        if username is not None and password is not None:
            self.client.username_pw_set(username, password)
        self.hostname = hostname
        self.port = port
        if use_tls and (ca_certs is not None):
            self.client.tls_set(
                ca_certs=ca_certs, cert_reqs=ssl.CERT_REQUIRED,
                tls_version=tls_version
            )

        if topics:
            self.topics = {
                topic: params for (topic, params) in topics.items()
            }
        else:
            self.topics = {}

        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.ping_mid = None
        self.disconnected = self.loop.create_future()

    def on_connect(self, client, userdata, flags, rc):
        """When the client connects, subscribe to the topic."""
        if rc != 0:
            logger.error('Bad connection, returned code: {}'.format(rc))
            return
        for (topic, params) in self.topics.items():
            if params['subscribe']:
                for topic_path in self.get_topic_paths(topic):
                    logger.info(
                        'Subscribing to {} topic...'.format(topic_path)
                    )
                    client.subscribe(topic_path, qos=params['qos'])
        self.add_topic_handlers()
        logger.info('Finished subscribing to topics!')
        self.publish_message(
            connect_topic, self.client_name, local_namespace=False
        )

    def on_message(self, client, userdata, msg):
        """When the client receives a message, handle it."""
        if (
            msg.topic in self.topics
            and self.topics[msg.topic].get('log', False)
        ):
            logger.info(
                'Got message on topic {}: {}'.format(msg.topic, msg.payload)
            )

    def on_disconnect(self, client, userdata, rc):
        """When the client disconnects, handle it."""
        if rc != 0:
            logger.error('Disconnected, returned code: {}'.format(rc))
        self.disconnected.set_result(rc)

    def on_publish(self, client, userdata, mid):
        """When the client publishes a message, handle it."""
        if mid == self.ping_mid:
            logger.debug('Ping {} published to broker'.format(mid))
            self.ping_mid = None

    def add_topic_handlers(self):
        """Add any topic handler message callbacks as needed."""
        pass

    def connect(self, reconnect=False):
        """Start the client connection."""
        if reconnect:
            self.client.reconnect()
        else:
            self.client.connect(self.hostname, self.port)
        self.client.socket().setsockopt(
            socket.SOL_SOCKET, socket.SO_SNDBUF, 2048
        )

    def on_run(self):
        """When the client starts the run loop, handle it."""
        pass

    def on_quit(self):
        """When the client quits the run loop, handle it."""
        pass

    async def attempt_reconnect(self):
        """Prepare the system for a reconnection attempt."""
        pass

    async def loop_until_connect(self, reconnect=False):
        """Repeatedly attempt to connect until successful."""
        while True:
            try:
                self.connect(reconnect=reconnect)
                self.disconnected = self.loop.create_future()
                break
            except socket.gaierror:
                logger.error(
                    'DNS lookup of hostname {} failed, trying again...'
                    .format(self.hostname)
                )
            except (ConnectionRefusedError, TimeoutError):
                logger.error(
                    'Broker server not available, trying again in {} sec...'
                    .format(self.ping_interval)
                )
                await asyncio.sleep(self.ping_interval)
            except OSError:
                logger.error(
                    'Internet connection not available, trying again...'
                    .format(self.ping_interval)
                )
                await self.attempt_reconnect()

        logger.info('Connected to {}:{}.'.format(self.hostname, self.port))

    async def run(self):
        """Run the client."""
        self.on_run()
        try:
            await self.loop_until_connect()
        except asyncio.CancelledError:
            self.on_quit()
            return

        while True:
            try:
                if self.disconnected.done() and self.disconnected.result():
                    logger.info('Reconnecting...')
                    await self.loop_until_connect(reconnect=True)
                await self.run_iteration()
            except asyncio.CancelledError:
                break

        logger.info('Disconnecting...')
        self.client.disconnect()
        await self.disconnected
        logger.info('Disconnected!')
        self.on_quit()

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        await asyncio.sleep(self.ping_interval - self.ping_timeout)
        message = self.publish_message(
            ping_topic, self.client_name, qos=1,
            local_namespace=self.client_name
        )[0]
        self.ping_mid = message.mid
        await asyncio.sleep(self.ping_timeout)
        if self.ping_mid is not None:
            self.on_disconnect(self.client, None, 1)
            self.ping_mid = None

    def get_target_names(self, topic):
        return self.target_names

    def get_topic_paths(self, topic, local_namespace=None):
        if local_namespace is False:
            return [topic]
        elif local_namespace is True:
            return build_topic_paths(self.get_target_names(topic), topic)
        elif local_namespace is None:
            if topic in self.topics and self.topics[topic]['local_namespace']:
                return build_topic_paths(self.get_target_names(topic), topic)
            else:
                return [topic]
        else:
            return ['{}/{}'.format(local_namespace, topic)]

    def publish_message(self, topic, payload, qos=2, local_namespace=None):
        """Publish a message."""
        return [
            self.client.publish(topic_path, payload, qos)
            for topic_path in self.get_topic_paths(
                topic, local_namespace=local_namespace
            )
        ]
