"""Main page routes."""
from flask import Blueprint, render_template
from ..data import get_data, calculate_coverage_area

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Home page"""
    config, nodes, members = get_data()

    # Calculate stats
    stats = {
        'totalNodes': len(nodes),
        'totalMembers': len(members),
        'coverageArea': calculate_coverage_area(nodes)
    }

    return render_template('index.html', config=config, nodes=nodes, members=members, stats=stats)


@main_bp.route('/contact/')
def contact():
    """Contact page"""
    config, nodes, members = get_data()
    return render_template('contact.html', config=config)
