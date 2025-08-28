"""Data loading and processing functions."""
import json
import os
import logging
from math import cos, radians
from typing import Dict, List, Any, Tuple, Optional
from .supabase_service import supabase_service

ASSETS_DIR = 'assets'
logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file (config remains in JSON)"""
    try:
        with open(os.path.join(ASSETS_DIR, "data", "config.json"), 'r') as f:
            config = json.load(f)
            return config if isinstance(config, dict) else {}
    except FileNotFoundError:
        logger.error("config.json not found")
        return {}


def get_data() -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Load all data - config from JSON, nodes and members from Supabase"""
    config = load_config()
    nodes = supabase_service.get_nodes(include_private=False)  # Public nodes only
    members = supabase_service.get_members(include_private=False)  # Public members only

    return config, nodes, members


def calculate_coverage_area(nodes: List[Dict[str, Any]]) -> int:
    """Calculate approximate coverage area in km²"""
    if not nodes:
        return 0

    # Extract coordinates from new latitude/longitude fields
    coords = []
    for node in nodes:
        lat = node.get('latitude')
        lng = node.get('longitude')
        if lat is not None and lng is not None:
            coords.append((float(lat), float(lng)))

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
        'onlineNodes': len([node for node in nodes if node.get('is_online', True)]),
        'repeaterNodes': len([node for node in nodes if node.get('mesh_role') == 'repeater'])
    }


def find_node_by_id(nodes: List[Dict[str, Any]], area: str, node_id: str) -> Optional[Dict[str, Any]]:
    """Find a specific node by area and node_id"""
    # New format: {area}-{node_id}.ipnt.uk (e.g., "ip2-rep01.ipnt.uk")
    full_node_id = f"{area}-{node_id}.ipnt.uk"

    # Try to get from Supabase first
    node = supabase_service.get_node_by_id(full_node_id)
    if node:
        return node  # type: ignore[no-any-return]

    # Also check legacy format: {node_id}.{area}.ipnt.uk for backward compatibility
    legacy_node_id = f"{node_id}.{area}.ipnt.uk"
    node = supabase_service.get_node_by_id(legacy_node_id)
    if node:
        return node  # type: ignore[no-any-return]

    # Fallback to search in provided nodes list (for compatibility)
    return next((node for node in nodes if node['node_id'] == full_node_id or node['node_id'] == legacy_node_id or node['node_id'] == node_id), None)


def get_supabase_config() -> Dict[str, str]:
    """Get Supabase configuration for client-side real-time updates"""
    return {
        'url': os.getenv('SUPABASE_URL', ''),
        'anon_key': os.getenv('SUPABASE_ANON_KEY', '')
    }
