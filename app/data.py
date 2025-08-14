"""Data loading and processing functions."""
import json
import os
from typing import Dict, List, Any, Tuple, Optional

ASSETS_DIR = 'assets'


def load_json_data(filename: str) -> Dict[str, Any]:
    """Load JSON data from the assets/data directory"""
    try:
        with open(os.path.join(ASSETS_DIR, "data", filename), 'r') as f:
            data: Dict[str, Any] = json.load(f)
            return data
    except FileNotFoundError:
        return {}


def get_data() -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Load all data files"""
    config = load_json_data('config.json')
    nodes_data = load_json_data('nodes.json')
    members_data = load_json_data('members.json')

    # Filter public nodes and members
    nodes = [node for node in nodes_data.get('nodes', []) if node.get('isPublic', True)]
    members = [member for member in members_data.get('members', []) if member.get('isPublic', True)]

    return config, nodes, members


def calculate_coverage_area(nodes: List[Dict[str, Any]]) -> int:
    """Calculate approximate coverage area in km²"""
    if not nodes:
        return 0

    # Extract coordinates
    coords = []
    for node in nodes:
        if node.get('location') and node['location'].get('lat') and node['location'].get('lng'):
            coords.append((node['location']['lat'], node['location']['lng']))

    if not coords:
        return 0

    # Simple bounding box calculation
    lats = [coord[0] for coord in coords]
    lngs = [coord[1] for coord in coords]

    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)

    # Rough approximation of area in km²
    lat_diff = max_lat - min_lat
    lng_diff = max_lng - min_lng
    area = round(lat_diff * lng_diff * 12400)  # Rough conversion factor

    return int(max(area, 50))  # Minimum 50 km²


def calculate_node_stats(nodes: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate node statistics for the nodes page"""
    return {
        'totalNodes': len(nodes),
        'onlineNodes': len([node for node in nodes if node.get('isOnline', True)]),
        'repeaterNodes': len([node for node in nodes if node.get('meshRole') == 'repeater'])
    }


def find_node_by_id(nodes: List[Dict[str, Any]], area: str, node_id: str) -> Optional[Dict[str, Any]]:
    """Find a specific node by area and node_id"""
    full_node_id = f"{node_id}.{area}.ipnt.uk"
    return next((node for node in nodes if node['id'] == full_node_id or node['id'] == node_id), None)
