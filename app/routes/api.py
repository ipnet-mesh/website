"""API routes."""
from flask import Blueprint, jsonify
from werkzeug.wrappers import Response
from ..data import get_data

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/data')
def api_data() -> Response:
    """API endpoint to serve data as JSON"""
    config, nodes, members = get_data()
    response: Response = jsonify({
        'config': config,
        'nodes': nodes,
        'members': members
    })
    return response
