"""Member-related routes."""
from flask import Blueprint, render_template
from ..data import get_data

members_bp = Blueprint('members', __name__)


@members_bp.route('/members/')
def index() -> str:
    """Members page"""
    config, nodes, members_list = get_data()
    return render_template('members.html', config=config, nodes=nodes, members=members_list)
