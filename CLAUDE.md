# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based website for IPNet (Ipswich Mesh Network), a local MeshCore community group serving Ipswich, Suffolk, UK. The site displays mesh network nodes, member profiles, and provides community information with real-time updates via Supabase integration.

## Development Requirements

* ALWAYS activate the virtual environment (`<project-root>/.venv`) before running ANY commands
* ALWAYS add a new-line at the end of files you edit
* NEVER add Claude attribution to commit messages or documentation
* Project uses `pre-commit` hooks for code quality checks

## Architecture

### Backend (Flask)
- **Application Structure**: Modular Flask app with blueprints in `app/` directory
- **Entry Point**: `run.py` initializes and starts the Flask application
- **Routes**: `/` (home), `/nodes/` (with optional area/node_id), `/members/`, `/contact/`, `/api/data`
- **Database**: Supabase PostgreSQL for nodes and members data with real-time capabilities
- **Service Layer**: `app/supabase_service.py` handles all database operations (returns raw DB records)
- **Privacy filtering**: Database-level filtering with `is_public` column
- **Coverage calculation**: Simple bounding box algorithm using `latitude` and `longitude` fields
- **Removed Fields**: `frequency` and `power` fields have been removed from nodes table

### Frontend
- **Templates**: Jinja2 templates in `templates/` directory with base.html inheritance
- **Styling**: TailwindCSS with dark mode support, custom color scheme (primary: #10b981)
- **JavaScript**: Vanilla JS in `assets/js/app.js` for data loading and client-side functionality
- **Alpine.js**: Used for dark mode state management
- **Real-time Updates**: `assets/js/supabase-realtime.js` for live data synchronization
- **Supabase Client**: JavaScript client for real-time database subscriptions

### Database Structure (Supabase PostgreSQL)
- **members table**: User profiles with social links, bio, and privacy controls
- **nodes table**: Mesh network node data with separate location fields (latitude, longitude, location_description), hardware specs, status
- **Raw Database Structure**: Templates and JavaScript use native Supabase field names directly (no data transformation layer)
- **Field Naming**: Uses database column names like `node_id`, `is_online`, `mesh_role`, `member_id`, etc.
- **Real-time subscriptions**: Live updates for node status changes and new data
- **Row Level Security**: Database-level privacy controls with `is_public` filtering
- **config.json**: Site configuration remains in JSON file (contact info, theme settings)

## Development Commands

### CSS Build
```bash
# Development (watch mode)
npm run build-css

# Production (minified)
npm run build-css-prod
```

### Flask Application
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up Supabase (required)
# Update .env with Supabase credentials
# Run database migration: python db/migrate_data.py
# If migrating from previous schema: run db/migrate_location_fields.sql in Supabase

# Run development server
python run.py
# Server runs on http://0.0.0.0:8000 with debug=True
```

## Key Files

- **run.py**: Application entry point and server initialization
- **app/**: Main Flask application directory with blueprints and services
- **app/supabase_service.py**: Database service layer for all Supabase operations
- **db/schema.sql**: Database schema for Supabase tables
- **db/migrate_data.py**: Migration script from JSON to Supabase
- **db/migrate_location_fields.sql**: Schema migration for location field changes
- **assets/data/config.json**: Site configuration (only config remains in JSON)
- **templates/base.html**: Main template with meta tags, dark mode, Supabase integration
- **assets/js/app.js**: Client-side data loading and JavaScript functionality
- **assets/js/supabase-realtime.js**: Real-time database subscriptions
- **tailwind.config.js**: TailwindCSS configuration with custom colors and dark mode
- **assets/css/input.css**: TailwindCSS source file
- **assets/css/output.css**: Generated CSS (do not edit directly)

## Data Management

Data is stored in Supabase PostgreSQL database:
1. **Real-time Updates**: Changes automatically sync across all connected clients
2. **Privacy Controls**: Use `is_public` column to control data visibility
3. **Node Management**: Update node status, location, and hardware info via database
4. **Member Profiles**: Manage member information, avatars, and social links
5. **Database Access**: Use `app/supabase_service.py` for all database operations
6. **Node IDs**: Follow format `{shortname}.{area}.ipnt.uk`
7. **Geographic Data**: Store coordinates in separate `latitude`, `longitude`, and `location_description` columns
8. **Raw Field Access**: Templates and JavaScript access database fields directly (e.g., `node.latitude`, `node.is_online`, `member.member_id`)
9. **Site Configuration**: `assets/data/config.json` remains for theme and contact info

## Deployment Notes

- **Database**: Requires Supabase project with proper environment variables
- **Real-time**: Supabase real-time subscriptions work automatically in browser
- **Static assets**: Served from `assets/` directory
- **Templates**: Served from `templates/` directory
- **API endpoint**: `/api/data` serves all data from Supabase
- **URL structure**: Supports both full paths and short redirects for individual nodes
- **Environment**: Set `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_KEY`
