"""External API client for fetching node data."""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_DIR = os.path.join('instance', 'cache', 'api')
CACHE_FILE = os.path.join(CACHE_DIR, 'nodes.json')
CACHE_TTL_MINUTES = 5  # Refresh cache every 5 minutes

_cache: Dict[str, Any] = {
    'nodes': [],
    'last_updated': None,
    'expires_at': None
}


def get_api_config() -> Tuple[Optional[str], Optional[str]]:
    """Get API configuration from environment."""
    api_url = os.environ.get('API_URL')
    api_key = os.environ.get('API_KEY')
    return api_url, api_key


def transform_api_node(api_node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform API node format to internal format."""
    tags = api_node.get('tags', {})

    # Skip nodes without tags (no metadata available)
    if not tags:
        return None

    # Use tags.node_id as primary ID, fallback to API name
    node_id = tags.get('node_id') or api_node.get('name')
    if not node_id:
        return None

    location = tags.get('location', {})

    return {
        'id': node_id,
        'publicKey': api_node.get('public_key', ''),
        'name': tags.get('friendly_name') or api_node.get('name') or node_id,
        'memberId': tags.get('member_id', ''),
        'area': tags.get('area', ''),
        'location': {
            'lat': location.get('latitude'),
            'lng': location.get('longitude'),
            'description': tags.get('location_description', '')
        },
        'hardware': tags.get('hardware', 'Unknown'),
        'antenna': tags.get('antenna', ''),
        'elevation': tags.get('elevation', 0),
        'showOnMap': tags.get('show_on_map', False),
        'isPublic': tags.get('is_public', False),
        'isOnline': tags.get('is_online', False),
        'isTesting': tags.get('is_testing', False),
        'meshRole': tags.get('mesh_role', 'unknown'),
        'lastSeen': api_node.get('last_seen'),
        'firstSeen': api_node.get('first_seen'),
        'channels': []
    }


def fetch_nodes_from_api() -> Optional[List[Dict[str, Any]]]:
    """Fetch nodes from external API."""
    api_url, api_key = get_api_config()

    if not api_url:
        logger.warning("API_URL not configured")
        return None

    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    try:
        # Fetch all nodes (API supports pagination)
        url = f"{api_url}/api/v1/nodes?limit=100&offset=0&sort_by=last_seen&order=desc"
        logger.info(f"Fetching nodes from API: {url}")
        response = requests.get(url, headers=headers, timeout=10)

        # Log response status
        logger.info(f"API response status: {response.status_code}")

        # Check for non-success status codes
        if response.status_code != 200:
            logger.error(f"API returned status {response.status_code}: {response.text[:200]}")
            return None

        # Check for empty response
        if not response.text or not response.text.strip():
            logger.error("API returned empty response")
            return None

        # Try to parse JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API JSON response: {e}")
            logger.error(f"Response content (first 500 chars): {response.text[:500]}")
            return None

        # Check for API error response
        if 'error' in data:
            logger.error(f"API error: {data.get('error')} - {data.get('detail', '')}")
            return None

        api_nodes = data.get('nodes', [])

        # Transform to internal format
        nodes = []
        for api_node in api_nodes:
            transformed = transform_api_node(api_node)
            if transformed:
                nodes.append(transformed)

        logger.info(f"Fetched {len(nodes)} nodes from API (total in response: {len(api_nodes)})")
        return nodes

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch nodes from API: {e}")
        return None


def save_cache(nodes: List[Dict[str, Any]]) -> None:
    """Save nodes to cache file."""
    cache_data = {
        'lastUpdated': datetime.utcnow().isoformat() + 'Z',
        'nodes': nodes
    }
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
        logger.info(f"Cache saved with {len(nodes)} nodes")
    except IOError as e:
        logger.error(f"Failed to save cache: {e}")


def load_cache() -> List[Dict[str, Any]]:
    """Load nodes from cache file."""
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            nodes: List[Dict[str, Any]] = data.get('nodes', [])
            logger.info(f"Loaded {len(nodes)} nodes from cache file")
            return nodes
    except (IOError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to load cache: {e}")
        return []


def get_nodes() -> List[Dict[str, Any]]:
    """Get nodes with caching strategy.

    Priority order:
    1. Memory cache (if valid)
    2. API fetch (updates cache)
    3. File cache (if API fails)
    """
    global _cache

    now = datetime.utcnow()

    # Check if memory cache is valid
    if _cache['expires_at'] and now < _cache['expires_at'] and _cache['nodes']:
        logger.debug("Using memory cache")
        cached_nodes: List[Dict[str, Any]] = _cache['nodes']
        return cached_nodes

    # Try to fetch from API
    nodes = fetch_nodes_from_api()

    if nodes is not None and len(nodes) > 0:
        # Update memory cache
        _cache['nodes'] = nodes
        _cache['last_updated'] = now
        _cache['expires_at'] = now + timedelta(minutes=CACHE_TTL_MINUTES)

        # Persist to file cache
        save_cache(nodes)

        return nodes

    # API failed or returned empty, try file cache
    cached_nodes = load_cache()
    if cached_nodes:
        logger.info("Using file cache due to API failure")
        _cache['nodes'] = cached_nodes
        _cache['expires_at'] = now + timedelta(minutes=1)  # Shorter TTL for fallback
        return cached_nodes

    # Nothing available
    logger.error("No nodes available from API or cache")
    return []
