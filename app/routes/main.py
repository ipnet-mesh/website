"""Main page routes."""
from flask import Blueprint, render_template, Response
from ..data import get_data, calculate_coverage_area, get_supabase_config, load_config

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home() -> str:
    """Home page"""
    config, nodes, members = get_data()

    # Calculate stats
    stats = {
        'totalNodes': len(nodes),
        'totalMembers': len(members),
        'coverageArea': calculate_coverage_area(nodes)
    }

    return render_template('index.html', config=config, nodes=nodes, members=members, stats=stats, supabase_config=get_supabase_config())


@main_bp.route('/contact/')
def contact() -> str:
    """Contact page"""
    config = load_config()
    return render_template('contact.html', config=config)
