"""Data loading and processing functions."""
import json
import os
from math import cos, radians
from typing import Any, Dict, List, Optional, Tuple

from .api_client import get_nodes as get_nodes_from_api

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
    members_data = load_json_data('members.json')

    # Get nodes from API (with caching)
    all_nodes = get_nodes_from_api()

    # Filter public nodes and members
    nodes = [node for node in all_nodes if node.get('isPublic', True)]
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

    # Convert degrees to kilometers
    # 1 degree of latitude ≈ 111 km everywhere
    # 1 degree of longitude varies by latitude: ≈ 111 * cos(latitude) km
    lat_diff_km = (max_lat - min_lat) * 111

    # Use average latitude for longitude conversion
    avg_lat = (min_lat + max_lat) / 2
    lng_diff_km = (max_lng - min_lng) * 111 * abs(cos(radians(avg_lat)))

    # Calculate area in km²
    area = round(lat_diff_km * lng_diff_km)

    return int(max(area, 1))  # Minimum 1 km²


def calculate_node_stats(nodes: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate node statistics for the nodes page"""
    return {
        'totalNodes': len(nodes),
        'onlineNodes': len([node for node in nodes if node.get('isOnline', True)]),
        'repeaterNodes': len([node for node in nodes if node.get('meshRole') == 'repeater'])
    }


def find_node_by_id(nodes: List[Dict[str, Any]], area: str, node_id: str) -> Optional[Dict[str, Any]]:
    """Find a specific node by area and node_id"""
    # New format: {area}-{node_id}.ipnt.uk (e.g., "ip2-rep01.ipnt.uk")
    full_node_id = f"{area}-{node_id}.ipnt.uk"
    # Also check legacy format: {node_id}.{area}.ipnt.uk for backward compatibility
    legacy_node_id = f"{node_id}.{area}.ipnt.uk"
    return next((node for node in nodes if node['id'] == full_node_id or node['id'] == legacy_node_id or node['id'] == node_id), None)


def find_node_by_public_key(nodes: List[Dict[str, Any]], public_key: str) -> Optional[Dict[str, Any]]:
    """Find a specific node by its public key (64 char hex)"""
    return next((node for node in nodes if node.get('publicKey') == public_key), None)
