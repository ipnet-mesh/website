"""MQTT client module for connecting to broker and handling messages."""
import os
import ssl
import json
import logging
import uuid
from typing import Optional, Callable, Dict, Any
import paho.mqtt.client as mqtt
from flask_socketio import SocketIO

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT client with authentication and WebSocket integration."""

    def __init__(self, socketio: Optional[SocketIO] = None):
        self.client: Optional[mqtt.Client] = None
        self.socketio = socketio
        self.is_connected = False

        # MQTT configuration from environment variables
        self.broker_host = os.getenv('MQTT_BROKER_HOST')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', '1883'))
        self.username = os.getenv('MQTT_USERNAME')
        self.password = os.getenv('MQTT_PASSWORD')
        self.use_tls = os.getenv('MQTT_USE_TLS', 'false').lower() == 'true'
        self.ca_cert = os.getenv('MQTT_CA_CERT')
        self.client_cert = os.getenv('MQTT_CLIENT_CERT')
        self.client_key = os.getenv('MQTT_CLIENT_KEY')
        # Generate unique client ID for HA deployments
        base_client_id = os.getenv('MQTT_CLIENT_ID', 'ipnet-website')
        unique_suffix = str(uuid.uuid4())[:8]  # First 8 chars of UUID
        self.client_id = f"{base_client_id}-{unique_suffix}"
        self.keepalive = int(os.getenv('MQTT_KEEPALIVE', '120'))

        # Default topics to subscribe to
        self.default_topics = [
            'ipnet/+/status',
            'ipnet/+/metrics',
            'ipnet/network/topology',
            'ipnet/alerts/+'
        ]

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int) -> None:
        """Callback for when client connects to MQTT broker."""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.is_connected = True

            # Subscribe to default topics
            for topic in self.default_topics:
                client.subscribe(topic)
                logger.debug(f"Subscribed to topic: {topic}")

            # Emit connection status to WebSocket clients
            if self.socketio:
                self.socketio.emit('mqtt_status', {'connected': True})
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")
            self.is_connected = False
            if self.socketio:
                self.socketio.emit('mqtt_status', {'connected': False, 'error': f'Connection failed: {rc}'})

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """Callback for when client disconnects from MQTT broker."""
        logger.warning(f"Disconnected from MQTT broker, return code {rc}")
        self.is_connected = False
        if self.socketio:
            self.socketio.emit('mqtt_status', {'connected': False})

    def _on_message(self, client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
        """Callback for when a message is received from MQTT broker."""
        try:
            topic = message.topic
            payload = message.payload.decode('utf-8')

            logger.debug(f"Received MQTT message - Topic: {topic}, Payload: {payload}")

            # Try to parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = payload

            # Forward message to WebSocket clients
            if self.socketio:
                self.socketio.emit('mqtt_message', {
                    'topic': topic,
                    'data': data,
                    'timestamp': message.timestamp if hasattr(message, 'timestamp') else None
                })

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def connect(self) -> bool:
        """Connect to MQTT broker with authentication."""
        if not self.broker_host:
            logger.error("MQTT_BROKER_HOST environment variable not set")
            return False

        try:
            # Create MQTT client
            self.client = mqtt.Client(client_id=self.client_id, clean_session=True)

            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            # Set authentication if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
                logger.info("MQTT username/password authentication configured")

            # Set TLS configuration if enabled
            if self.use_tls:
                context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

                if self.ca_cert:
                    context.load_verify_locations(self.ca_cert)

                if self.client_cert and self.client_key:
                    context.load_cert_chain(self.client_cert, self.client_key)

                self.client.tls_set_context(context)
                logger.info("MQTT TLS configuration enabled")

            # Connect to broker
            self.client.connect(self.broker_host, self.broker_port, keepalive=self.keepalive)

            # Start network loop in background
            self.client.loop_start()

            logger.info(f"Attempting to connect to MQTT broker at {self.broker_host}:{self.broker_port}")
            return True

        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if self.client and self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")

    def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> bool:
        """Publish message to MQTT topic."""
        if not self.client or not self.is_connected:
            logger.error("MQTT client not connected")
            return False

        try:
            result = self.client.publish(topic, payload, qos, retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published message to topic {topic}")
                return True
            else:
                logger.error(f"Failed to publish message to topic {topic}, return code {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing MQTT message: {e}")
            return False

    def subscribe(self, topic: str, qos: int = 0) -> bool:
        """Subscribe to additional MQTT topic."""
        if not self.client or not self.is_connected:
            logger.error("MQTT client not connected")
            return False

        try:
            result = self.client.subscribe(topic, qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Subscribed to topic: {topic}")
                return True
            else:
                logger.error(f"Failed to subscribe to topic {topic}, return code {result[0]}")
                return False
        except Exception as e:
            logger.error(f"Error subscribing to MQTT topic: {e}")
            return False

    def unsubscribe(self, topic: str) -> bool:
        """Unsubscribe from MQTT topic."""
        if not self.client or not self.is_connected:
            logger.error("MQTT client not connected")
            return False

        try:
            result = self.client.unsubscribe(topic)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Unsubscribed from topic: {topic}")
                return True
            else:
                logger.error(f"Failed to unsubscribe from topic {topic}, return code {result[0]}")
                return False
        except Exception as e:
            logger.error(f"Error unsubscribing from MQTT topic: {e}")
            return False
