# IPNet Community Website

[![Docker Build and Push](https://github.com/ipnet-mesh/website/actions/workflows/docker-build.yml/badge.svg)](https://github.com/ipnet-mesh/website/actions/workflows/docker-build.yml)

A Flask-based community website for IPNet (Ipswich Mesh Network), a local MeshCore community group serving Ipswich, Suffolk, UK. The site displays mesh network nodes, member profiles, and provides community information with interactive maps and statistics.

## Features

- **Interactive Node Map**: Geographic display of mesh network nodes with detailed information
- **Member Profiles**: Community member directory with avatars and contact preferences
- **Network Statistics**: Real-time coverage area calculations and network metrics
- **Supabase Integration**: PostgreSQL database with real-time updates and scalable data management
- **Live Data Synchronization**: Real-time updates across all connected clients
- **Dark Mode Support**: User-configurable theme with persistent preferences
- **Mobile Responsive**: Optimized for all device sizes using TailwindCSS
- **Privacy Controls**: Configurable visibility for nodes and members


## Quick Start

## Architecture

### Backend (Flask)
- **Application Structure**: Modular Flask app with blueprints for routes and services
- **Routes**: `/` (home), `/nodes/` (with optional area/node_id), `/members/`, `/contact/`, `/api/data`
- **Data Management**: Supabase PostgreSQL database with real-time capabilities
- **Service Layer**: Dedicated Supabase service for all database operations
- **WSGI Server**: Gunicorn for production deployments

### Frontend
- **Templates**: Jinja2 templates with inheritance from `templates/base.html`
- **Styling**: TailwindCSS with custom color scheme and dark mode
- **JavaScript**: Vanilla JS for data loading and client-side functionality
- **Alpine.js**: Lightweight reactivity for UI state management
- **Real-time Updates**: Supabase JavaScript client for live data synchronization

### Database Structure
- **PostgreSQL**: Hosted on Supabase with real-time capabilities
- **Members Table**: User profiles with social links and privacy controls
- **Nodes Table**: Mesh network node data with separate location fields (latitude, longitude, location_description)
- **Raw Database Structure**: Templates and JavaScript use native Supabase field names directly (no data transformation)
- **Real-time Subscriptions**: Live updates for node status changes and new data
- **Row Level Security**: Database-level privacy and access controls

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+ (LTS)
- Supabase account and project

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ipnet-mesh/website.git
   cd website
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Set up Supabase**

   Create a new Supabase project:
   - Go to https://supabase.com/dashboard
   - Click "New Project" and configure your project
   - Get your project credentials from **Settings** > **API**

   Update your `.env` file:
   ```bash
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-public-key
   SUPABASE_SERVICE_KEY=your-service-role-key
   ```

   Create database schema:
   - In Supabase dashboard, go to **SQL Editor**
   - Copy and run the schema from `db/schema.sql`

   If migrating from existing JSON data:
   ```bash
   python db/migrate_data.py
   ```

5. **Build CSS assets**
   ```bash
   # Development (watch mode)
   npm run build-css

   # Or production build
   npm run build-css-prod
   ```

6. **Run the Flask application**
   ```bash
   python run.py
   ```

   The application will be available at http://localhost:8000

### Development Workflow

#### CSS Development
```bash
# Watch for changes and rebuild automatically
npm run build-css

# Build minified CSS for production
npm run build-css-prod
```

#### Database Management

Data is stored in Supabase PostgreSQL database:
- **Real-time Updates**: Changes sync automatically across all clients
- **Privacy Controls**: Use `is_public` flag to control visibility
- **Node Status**: Update node online status via database
- **Member Profiles**: Manage member information with social links
- **Geographic Data**: Store coordinates in separate `latitude`, `longitude`, and `location_description` columns
- **Raw Field Names**: Templates and JavaScript use database field names directly (`node_id`, `is_online`, `mesh_role`, etc.)

#### File Structure
```
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
├── tailwind.config.js      # TailwindCSS configuration
├── app/
│   ├── __init__.py         # Flask application factory
│   ├── data.py             # Data loading functions
│   ├── supabase_service.py # Database service layer
│   └── routes/             # Route blueprints
├── db/
│   ├── schema.sql          # Database schema
│   ├── migrate_data.py     # Data migration script
│   └── migrate_location_fields.sql # Schema migration for location fields
├── assets/
│   ├── css/
│   │   ├── input.css       # TailwindCSS source
│   │   └── output.css      # Generated CSS (do not edit)
│   ├── data/
│   │   └── config.json     # Site configuration (JSON only)
│   ├── js/
│   │   ├── app.js          # Client-side JavaScript
│   │   └── supabase-realtime.js # Real-time updates
│   └── images/             # Static assets
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Homepage
│   ├── nodes.html          # Nodes page
│   ├── members.html        # Members page
│   └── contact.html        # Contact page
└── CLAUDE.md               # Claude Code instructions
```

## Deployment

For traditional deployments:

```bash
# Install dependencies
pip install -r requirements.txt
npm install && npm run build-css-prod

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

## API Endpoints

- `GET /`: Homepage with network statistics
- `GET /nodes/`: All nodes page
- `GET /nodes/<area>/<node_id>`: Individual node view
- `GET /members/`: Members directory
- `GET /contact/`: Contact information
- `GET /api/data`: JSON API for all data

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test locally
4. Build CSS and test the application: `npm run build-css-prod && python run.py`
5. Commit changes: `git commit -am 'Add new feature'`
6. Push to branch: `git push origin feature/new-feature`
7. Create a Pull Request

## License

This project is open source and available under the [GPL-3.0 License](LICENSE).
