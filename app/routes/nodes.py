"""Node-related routes."""
from flask import Blueprint, render_template, redirect, url_for
from ..data import get_data, calculate_node_stats, find_node_by_id

nodes_bp = Blueprint('nodes', __name__)


@nodes_bp.route('/<area>/<node_id>')
def redirect_to_nodes(area, node_id):
    """Redirect short URL format to full nodes URL"""
    return redirect(url_for('nodes.index', area=area, node_id=node_id), code=301)


@nodes_bp.route('/nodes/')
@nodes_bp.route('/nodes/<area>/<node_id>')
def index(area=None, node_id=None):
    """Nodes page with optional individual node view"""
    config, nodes, members = get_data()

    current_node = None
    if area and node_id:
        current_node = find_node_by_id(nodes, area, node_id)

    # Calculate node statistics for list view
    node_stats = None
    if not current_node:
        node_stats = calculate_node_stats(nodes)

    return render_template('nodes.html',
                         config=config,
                         nodes=nodes,
                         members=members,
                         current_node=current_node,
                         showing_individual_node=current_node is not None,
                         node_stats=node_stats)
