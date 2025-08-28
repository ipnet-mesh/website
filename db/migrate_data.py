#!/usr/bin/env python3
"""
Migration script to transfer data from JSON files to Supabase.
Run this script after setting up your Supabase project and configuring environment variables.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Create and return Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")

    return create_client(url, key)

def load_json_data() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Load data from JSON files."""
    # Get the script's directory and navigate to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "assets" / "data"

    # Load nodes data
    with open(data_dir / "nodes.json", "r") as f:
        nodes_data = json.load(f)

    # Load members data
    with open(data_dir / "members.json", "r") as f:
        members_data = json.load(f)

    return nodes_data, members_data

def migrate_members(supabase: Client, members_data: Dict[str, Any]) -> None:
    """Migrate members data to Supabase."""
    print("Migrating members...")

    members_to_insert = []

    for member in members_data["members"]:
        # Transform member data for database
        member_record = {
            "member_id": member["id"],
            "name": member["name"],
            "join_date": member.get("joinDate"),
            "location": member.get("location"),
            "avatar": member.get("avatar"),
            "bio": member.get("bio"),
            "contact_preference": member.get("contactPreference"),
            "is_public": member.get("isPublic", True),
            "node_name": member.get("nodeName"),
            "node_public_key": member.get("nodePublicKey"),
            "social_links": member.get("socialLinks", {})
        }

        members_to_insert.append(member_record)

    # Insert members in batches
    batch_size = 100
    for i in range(0, len(members_to_insert), batch_size):
        batch = members_to_insert[i:i + batch_size]
        try:
            result = supabase.table("members").insert(batch).execute()
            print(f"  Inserted {len(batch)} members (batch {i//batch_size + 1})")
        except Exception as e:
            print(f"  Error inserting members batch {i//batch_size + 1}: {e}")
            # Continue with next batch

    print(f"Members migration completed: {len(members_to_insert)} total records")

def migrate_nodes(supabase: Client, nodes_data: Dict[str, Any]) -> None:
    """Migrate nodes data to Supabase."""
    print("Migrating nodes...")

    nodes_to_insert = []

    for node in nodes_data["nodes"]:
        # Extract location data
        location = node.get("location", {})

        # Transform node data for database
        node_record = {
            "node_id": node["id"],
            "public_key": node.get("publicKey"),
            "name": node["name"],
            "member_id": node.get("memberId"),
            "area": node["area"],
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
            "location_description": location.get("description"),
            "hardware": node.get("hardware"),
            "antenna": node.get("antenna"),
            "elevation": node.get("elevation"),
            "show_on_map": node.get("showOnMap", True),
            "is_public": node.get("isPublic", True),
            "is_online": node.get("isOnline", False),
            "is_testing": node.get("isTesting", False),
            "last_seen": node.get("lastSeen"),
            "mesh_role": node.get("meshRole")
        }

        nodes_to_insert.append(node_record)

    # Insert nodes in batches
    batch_size = 100
    for i in range(0, len(nodes_to_insert), batch_size):
        batch = nodes_to_insert[i:i + batch_size]
        try:
            result = supabase.table("nodes").insert(batch).execute()
            print(f"  Inserted {len(batch)} nodes (batch {i//batch_size + 1})")
        except Exception as e:
            print(f"  Error inserting nodes batch {i//batch_size + 1}: {e}")
            # Continue with next batch

    print(f"Nodes migration completed: {len(nodes_to_insert)} total records")

def verify_migration(supabase: Client) -> None:
    """Verify the migration by counting records."""
    print("\nVerifying migration...")

    # Count members
    members_result = supabase.table("members").select("*", count="exact").execute()
    members_count = members_result.count if hasattr(members_result, 'count') else len(members_result.data)
    print(f"  Members in database: {members_count}")

    # Count nodes
    nodes_result = supabase.table("nodes").select("*", count="exact").execute()
    nodes_count = nodes_result.count if hasattr(nodes_result, 'count') else len(nodes_result.data)
    print(f"  Nodes in database: {nodes_count}")

    # Show sample records
    if members_result.data:
        print(f"  Sample member: {members_result.data[0]['name']} (ID: {members_result.data[0]['member_id']})")

    if nodes_result.data:
        print(f"  Sample node: {nodes_result.data[0]['name']} (ID: {nodes_result.data[0]['node_id']})")

def main():
    """Main migration function."""
    print("IPNet Data Migration to Supabase")
    print("=" * 40)

    try:
        # Initialize Supabase client
        print("Connecting to Supabase...")
        supabase = get_supabase_client()
        print("✓ Connected to Supabase")

        # Load JSON data
        print("Loading JSON data...")
        nodes_data, members_data = load_json_data()
        print(f"✓ Loaded {len(members_data['members'])} members and {len(nodes_data['nodes'])} nodes")

        # Migrate members first (nodes reference members)
        migrate_members(supabase, members_data)

        # Migrate nodes
        migrate_nodes(supabase, nodes_data)

        # Verify migration
        verify_migration(supabase)

        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update your Supabase environment variables in .env")
        print("2. Test the Flask application with Supabase integration")
        print("3. Consider setting up Supabase real-time subscriptions")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
