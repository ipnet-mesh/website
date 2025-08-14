"""API routes."""
from flask import Blueprint, jsonify
from ..data import get_data

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/data')
def api_data():
    """API endpoint to serve data as JSON"""
    config, nodes, members = get_data()
    return jsonify({
        'config': config,
        'nodes': nodes,
        'members': members
    })
