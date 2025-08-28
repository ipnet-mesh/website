"""
Supabase data service for IPNet website.
Handles all database operations for nodes and members.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from postgrest.exceptions import APIError

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service class for Supabase database operations."""

    def __init__(self) -> None:
        """Initialize Supabase client."""
        self.client: Optional[Client] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Supabase client with environment variables."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")  # Use anon key for regular operations

        if not url or not key:
            logger.warning("SUPABASE_URL or SUPABASE_ANON_KEY not configured, using fallback to JSON files")
            return

        try:
            self.client = create_client(url, key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Check if Supabase client is connected."""
        return self.client is not None

    def get_members(self, include_private: bool = False) -> List[Any]:
        """
        Get all members from database.

        Args:
            include_private: Include private members (default: False)

        Returns:
            List of member dictionaries
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return []

        try:
            query = self.client.table("members").select("*")

            if not include_private:
                query = query.eq("is_public", True)

            result = query.order("name").execute()

            logger.debug(f"Retrieved {len(result.data)} members from database")
            return result.data  # type: ignore[no-any-return]

        except APIError as e:
            logger.error(f"Supabase API error getting members: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting members: {e}")
            return []

    def get_nodes(self, include_private: bool = False) -> List[Any]:
        """
        Get all nodes from database.

        Args:
            include_private: Include private nodes (default: False)

        Returns:
            List of node dictionaries
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return []

        try:
            query = self.client.table("nodes").select("*")

            if not include_private:
                query = query.eq("is_public", True)

            result = query.order("area, node_id").execute()

            logger.debug(f"Retrieved {len(result.data)} nodes from database")
            return result.data  # type: ignore[no-any-return]

        except APIError as e:
            logger.error(f"Supabase API error getting nodes: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting nodes: {e}")
            return []

    def get_node_by_id(self, node_id: str) -> Optional[Any]:
        """
        Get a specific node by ID.

        Args:
            node_id: The node ID to search for

        Returns:
            Node dictionary or None if not found
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None

        try:
            result = self.client.table("nodes").select("*").eq("node_id", node_id).eq("is_public", True).execute()

            if not result.data:
                return None

            node = result.data[0]

            logger.debug(f"Retrieved node: {node_id}")
            return node

        except APIError as e:
            logger.error(f"Supabase API error getting node {node_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting node {node_id}: {e}")
            return None

    def update_node_status(self, node_id: str, is_online: bool, last_seen: Optional[str] = None) -> bool:
        """
        Update node online status and last seen timestamp.

        Args:
            node_id: The node ID to update
            is_online: Online status
            last_seen: Last seen timestamp (optional)

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False

        try:
            update_data: Dict[str, Any] = {"is_online": is_online}
            if last_seen:
                update_data["last_seen"] = last_seen

            result = self.client.table("nodes").update(update_data).eq("node_id", node_id).execute()

            if result.data:
                logger.debug(f"Updated node status: {node_id} -> online: {is_online}")
                return True
            else:
                logger.warning(f"No node found to update: {node_id}")
                return False

        except APIError as e:
            logger.error(f"Supabase API error updating node {node_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating node {node_id}: {e}")
            return False

    def get_node_statistics(self) -> Dict[str, Any]:
        """
        Get node statistics for the homepage.

        Returns:
            Dictionary with statistics
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return {"totalNodes": 0, "onlineNodes": 0, "areas": []}

        try:
            # Get all public nodes
            result = self.client.table("nodes").select("*").eq("is_public", True).execute()
            nodes = result.data

            total_nodes = len(nodes)
            online_nodes = len([n for n in nodes if n.get("is_online", False)])
            areas = list(set(n["area"] for n in nodes if n["area"]))

            # Calculate coverage (simplified)
            if nodes:
                locations = [n["location"] for n in nodes if n.get("location") and n["location"].get("lat") and n["location"].get("lng")]
                if locations:
                    lats = [loc["lat"] for loc in locations]
                    lngs = [loc["lng"] for loc in locations]

                    # Simple bounding box calculation
                    coverage_km2 = abs((max(lats) - min(lats)) * (max(lngs) - min(lngs))) * 111 * 111  # Rough conversion
                else:
                    coverage_km2 = 0
            else:
                coverage_km2 = 0

            stats = {
                "totalNodes": total_nodes,
                "onlineNodes": online_nodes,
                "areas": sorted(areas),
                "coverageKm2": round(coverage_km2, 1)
            }

            logger.debug(f"Calculated node statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error calculating node statistics: {e}")
            return {"totalNodes": 0, "onlineNodes": 0, "areas": [], "coverageKm2": 0}


# Global instance
supabase_service = SupabaseService()
