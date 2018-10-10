"""MQTT client support for remote control."""
import asyncio
import logging
import socket

import paho.mqtt.client as mqtt

# Set up logging
logger = logging.getLogger(__name__)


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
        self, loop, hostname, port, username=None, password=None, topics=[]
    ):
        """Initialize client state."""
        self.loop = loop
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.enable_logger(logger=logger)
        self.helper = AsyncioHelper(self.loop, self.client)

        self.username = username
        self.password = password
        if username is not None and password is not None:
            self.client.username_pw_set(username, password)
        self.hostname = hostname
        self.port = port

        if topics:
            self.topics = [topic for topic in topics]

        self.disconnected = self.loop.create_future()
        self.got_message = None

    def on_connect(self, client, userdata, flags, rc):
        """When the client connects, subscribe to the topic."""
        logger.info('Subscribing to topics...')
        for topic in self.topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        """When the client receives a message, handle it."""
        if not self.got_message:
            logger.error('Got unexpected message: {}'.format(msg.decode()))
        else:
            self.got_message.set_result(msg.payload)

    def on_disconnect(self, client, userdata, rc):
        """When the client disconnects, handle it."""
        self.disconnected.set_result(rc)

    def connect(self):
        """Start the client connection."""
        self.client.connect(self.hostname, self.port)
        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

    async def run(self):
        """Run the client."""
        self.connect()

        while True:
            try:
                await self.run_iteration()
            except asyncio.CancelledError:
                break

        self.client.disconnect()
        logger.info('Disconnected: {}'.format(await self.disconnected))

    async def run_iteration(self):
        """Run one iteration of the run loop."""
        pass
