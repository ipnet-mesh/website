"""Application factory and configuration."""
from flask import Flask, request, redirect, url_for
from werkzeug.wrappers import Response
from flask_socketio import SocketIO
import os
import re
import logging
from typing import Optional, Dict, Any
from .mqtt_client import MQTTClient

ASSETS_DIR = 'assets'

# Global variables for SocketIO and MQTT client
socketio = None
mqtt_client = None

def create_app() -> Flask:
    """Create and configure the Flask application"""
    # Get the directory containing this file (app/__init__.py)
    app_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to get the project root directory
    project_root = os.path.dirname(app_dir)

    # Set paths relative to project root
    static_folder = os.path.join(project_root, ASSETS_DIR)
    template_folder = os.path.join(project_root, 'templates')

    app = Flask(__name__,
                static_folder=static_folder,
                template_folder=template_folder)

    # Initialize SocketIO
    global socketio, mqtt_client
    socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

    # Initialize MQTT client
    mqtt_client = MQTTClient(socketio)

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Register blueprints
    from .routes.main import main_bp
    from .routes.nodes import nodes_bp
    from .routes.members import members_bp
    from .routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(nodes_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(api_bp)

    # Add build mode to template context
    @app.context_processor
    def inject_build_mode() -> Dict[str, Any]:
        """Make build mode available to all templates"""
        build_mode = os.environ.get('BUILD_MODE', '').lower()
        return {
            'build_mode': build_mode,
            'is_beta': build_mode == 'beta',
            'is_dev': build_mode == 'dev'
        }

    # Add subdomain detection middleware
    @app.before_request
    def handle_subdomain_redirect() -> Optional[Response]:
        """Detect subdomain patterns and redirect to appropriate node pages"""
        # Skip subdomain handling for static files and API calls
        if request.endpoint and (request.endpoint.startswith('static') or request.endpoint.startswith('api')):
            return None

        # Get the host header
        host = request.headers.get('Host', '')
        if not host:
            return None

        # Extract subdomain (everything before the first dot)
        subdomain_match = re.match(r'^([^.]+)\.', host)
        if not subdomain_match:
            return None

        subdomain = subdomain_match.group(1)

        # Skip common subdomains and localhost
        if subdomain in ['www', 'api', 'admin', 'localhost', '127', '192']:
            return None

        # Check for node pattern: area-nodeid (e.g., "ip2-rep01")
        node_pattern = re.match(r'^([a-zA-Z0-9]+)-([a-zA-Z0-9]+)$', subdomain)
        if node_pattern:
            area = node_pattern.group(1)
            node_id = node_pattern.group(2)

            # Strip subdomain and redirect to main domain
            # Get the main domain by removing everything before the first dot
            main_domain = re.sub(r'^[^.]+\.', '', host)

            # Build the redirect URL with the main domain
            node_url = url_for('nodes.index', area=area, node_id=node_id)
            redirect_url = f"{request.scheme}://{main_domain}{node_url}"

            return redirect(redirect_url, code=301)

        return None

    # SocketIO event handlers
    @socketio.on('connect')  # type: ignore
    def handle_connect() -> None:
        """Handle WebSocket connection."""
        logger.debug('WebSocket client connected')
        # Send current MQTT connection status
        if mqtt_client:
            socketio.emit('mqtt_status', {'connected': mqtt_client.is_connected})

    @socketio.on('disconnect')  # type: ignore
    def handle_disconnect() -> None:
        """Handle WebSocket disconnection."""
        logger.debug('WebSocket client disconnected')

    @socketio.on('mqtt_subscribe')  # type: ignore
    def handle_mqtt_subscribe(data: Dict[str, Any]) -> None:
        """Handle subscription to additional MQTT topics."""
        topic = data.get('topic')
        if topic and mqtt_client and mqtt_client.is_connected:
            success = mqtt_client.subscribe(topic)
            socketio.emit('mqtt_subscribe_result', {'topic': topic, 'success': success})

    @socketio.on('mqtt_unsubscribe')  # type: ignore
    def handle_mqtt_unsubscribe(data: Dict[str, Any]) -> None:
        """Handle unsubscription from MQTT topics."""
        topic = data.get('topic')
        if topic and mqtt_client and mqtt_client.is_connected:
            success = mqtt_client.unsubscribe(topic)
            socketio.emit('mqtt_unsubscribe_result', {'topic': topic, 'success': success})

    @socketio.on('mqtt_publish')  # type: ignore
    def handle_mqtt_publish(data: Dict[str, Any]) -> None:
        """Handle publishing messages to MQTT topics."""
        topic = data.get('topic')
        payload = data.get('payload', '')
        qos = data.get('qos', 0)
        retain = data.get('retain', False)

        if topic and mqtt_client and mqtt_client.is_connected:
            success = mqtt_client.publish(topic, payload, qos, retain)
            socketio.emit('mqtt_publish_result', {'topic': topic, 'success': success})

    # Start MQTT connection
    if mqtt_client:
        logger.info("Starting MQTT client connection...")
        mqtt_client.connect()

    return app
