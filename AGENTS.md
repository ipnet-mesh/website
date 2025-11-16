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
- **app.py**: Main Flask application with routing and data management
- Routes: `/` (home), `/nodes/` (with optional area/node_id), `/members/`, `/contact/`, `/api/data`
- Data loading: JSON files from `assets/data/` directory (config.json, nodes.json, members.json)
- Privacy filtering: Only displays items with `isPublic: true`
- Coverage calculation: Simple bounding box algorithm for geographic area estimation

### Frontend
- **Templates**: Jinja2 templates in `templates/` directory with base.html inheritance
- **Styling**: TailwindCSS with dark mode support, custom color scheme (primary: #10b981)
- **JavaScript**: Vanilla JS in `assets/js/app.js` for data loading and client-side functionality
- **Alpine.js**: Used for dark mode state management

### Data Structure
- **config.json**: Site configuration, contact info, theme settings, feature flags
- **nodes.json**: Mesh network node data with locations, hardware specs, public keys
- **members.json**: Member profiles with avatars, bios, contact preferences
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

- **app.py**: Flask routes and data processing logic
- **assets/data/**: JSON data files (config, nodes, members)
- **templates/base.html**: Main template with meta tags, dark mode setup
- **assets/js/app.js**: Client-side data loading and JavaScript functionality
- **tailwind.config.js**: TailwindCSS configuration with custom colors and dark mode
- **assets/css/input.css**: TailwindCSS source file
- **assets/css/output.css**: Generated CSS (do not edit directly)

## Data Management

When updating data:
1. Edit JSON files in `assets/data/` directory
2. Use `isPublic: false` to hide sensitive nodes/members
3. Node IDs follow format: `{shortname}.{area}.ipnt.uk`
4. Member avatars stored in `assets/images/avatars/`
5. Geographic coordinates required for coverage calculation

## Deployment Notes

- Static assets served from `assets/` directory
- Templates from `templates/` directory
- Supports both client-side and server-side data loading via `/api/data` endpoint
- URL structure supports both full paths and short redirects for individual nodes
