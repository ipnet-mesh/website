"""Application factory and configuration."""
from flask import Flask
import os

ASSETS_DIR = 'assets'


def create_app():
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

    return app
