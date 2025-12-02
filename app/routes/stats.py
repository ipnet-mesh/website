"""Stats-related routes."""
from typing import Any, Dict, List, Optional
from flask import Blueprint, render_template
from ..data import get_data, find_node_by_public_key
from ..api_client import get_advertisements

stats_bp = Blueprint('stats', __name__)


def enrich_advertisements(advertisements: List[Dict[str, Any]],
                          nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add node info to advertisements where available."""
    enriched = []
    for adv in advertisements:
        enriched_adv = dict(adv)
        node = find_node_by_public_key(nodes, adv.get('public_key', ''))
        if node:
            enriched_adv['node'] = node
        enriched.append(enriched_adv)
    return enriched


@stats_bp.route('/stats/')
def index() -> str:
    """Stats page with recent advertisements."""
    config, nodes, members = get_data()
    advertisements = get_advertisements(limit=20)
    advertisements = enrich_advertisements(advertisements, nodes)

    return render_template('stats.html',
                           config=config,
                           nodes=nodes,
                           members=members,
                           advertisements=advertisements)
