# AGENTS.md

This file provides guidance to AI Coding Agents when working with code in this repository.

## Project Overview

This is a Flask-based website for IPNet (Ipswich Mesh Network), a local MeshCore community group serving Ipswich, Suffolk, UK. The site displays mesh network nodes, member profiles, and provides community information.

## Development Requirements

* ALWAYS activate the virtual environment before running ANY commands
* ALWAYS add a new-line at the end of files you edit
* Project uses `pre-commit` hooks for code quality checks

## Architecture

### Backend (Flask)
- **app/**: Flask application package with blueprints
- Routes: `/` (home), `/nodes/` (with optional area/node_id), `/members/`, `/contact/`, `/api/data`
- **Node data**: Fetched from external API with file-based caching (`instance/cache/api/nodes.json`)
- **Static data**: JSON files from `assets/data/` directory (config.json, members.json)
- Privacy filtering: Only displays items with `isPublic: true`

### Frontend
- **Templates**: Jinja2 templates in `templates/` directory with base.html inheritance
- **Styling**: TailwindCSS with dark mode support, custom color scheme (primary: #10b981)
- **JavaScript**: Vanilla JS in `assets/js/app.js` for data loading and client-side functionality
- **Alpine.js**: Used for dark mode state management

### Data Structure
- **config.json**: Site configuration, contact info, theme settings, feature flags
- **members.json**: Member profiles with avatars, bios, contact preferences
- **Node data**: Fetched from external API (configured via `API_URL` environment variable)
- **Node privacy**: Filter by `isPublic` flag before display
- **URL routing**: Short URLs like `/<area>/<node_id>` redirect to full nodes page

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

# Run development server
python app.py
# Server runs on http://0.0.0.0:5000 with debug=True
```

## Key Files

- **app/**: Flask application package
  - **api_client.py**: External API client with caching for node data
  - **data.py**: Data loading and processing functions
  - **routes/**: Blueprint modules for each route group
- **assets/data/**: JSON data files (config.json, members.json)
- **templates/**: Jinja2 templates with base.html inheritance
- **assets/js/app.js**: Client-side JavaScript
- **assets/css/**: TailwindCSS source and generated files

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_URL` | Yes | Base URL for the MeshCore API |
| `API_KEY` | No | Bearer token for API authentication |

## Data Management

- Node data is fetched from the external API and cached locally
- Edit `assets/data/config.json` for site configuration
- Edit `assets/data/members.json` for member profiles
- Member avatars stored in `assets/images/avatars/`

## Deployment Notes

- Static assets served from `assets/` directory
- Templates from `templates/` directory
- Supports both client-side and server-side data loading via `/api/data` endpoint
- URL structure supports both full paths and short redirects for individual nodes
