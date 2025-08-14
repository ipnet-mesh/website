"""Application factory and configuration."""
from flask import Flask, request, redirect, url_for
from werkzeug.wrappers import Response
import os
import re
from typing import Optional, Dict, Any

ASSETS_DIR = 'assets'


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

    return app
