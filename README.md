# IPNet Community Website

[![Docker Build and Push](https://github.com/ipnet-mesh/website/actions/workflows/docker-build.yml/badge.svg)](https://github.com/ipnet-mesh/website/actions/workflows/docker-build.yml)

A Flask-based community website for IPNet (Ipswich Mesh Network), a local MeshCore community group serving Ipswich, Suffolk, UK. The site displays mesh network nodes, member profiles, and provides community information with interactive maps and statistics.

## Features

- **Interactive Node Map**: Geographic display of mesh network nodes with detailed information
- **Member Profiles**: Community member directory with avatars and contact preferences
- **Network Statistics**: Real-time coverage area calculations and network metrics
- **Dark Mode Support**: User-configurable theme with persistent preferences
- **Mobile Responsive**: Optimized for all device sizes using TailwindCSS
- **Privacy Controls**: Configurable visibility for nodes and members


## Quick Start

## Architecture

### Backend (Flask)
- **app/**: Flask application package with blueprints
- **Routes**: `/` (home), `/nodes/` (with optional area/node_id), `/members/`, `/contact/`, `/api/data`
- **Node Data**: Fetched from external API with file-based caching
- **WSGI Server**: Gunicorn for production deployments

### Frontend
- **Templates**: Jinja2 templates with inheritance from `templates/base.html`
- **Styling**: TailwindCSS with custom color scheme and dark mode
- **JavaScript**: Vanilla JS for data loading and client-side functionality
- **Alpine.js**: Lightweight reactivity for UI state management

### Data Structure
- **config.json**: Site configuration, contact info, theme settings
- **members.json**: Member profiles with avatars, bios, contact preferences
- **Node data**: Fetched from external API (configured via environment variables)

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+ (LTS)

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

4. **Build CSS assets**
   ```bash
   # Development (watch mode)
   npm run build-css

   # Or production build
   npm run build-css-prod
   ```

5. **Run the Flask application**
   ```bash
   python app.py
   ```

   The application will be available at http://localhost:5000

### Development Workflow

#### CSS Development
```bash
# Watch for changes and rebuild automatically
npm run build-css

# Build minified CSS for production
npm run build-css-prod
```

#### Environment Variables

Create a `.env` file with:
```
API_URL=https://api.example.com
API_KEY=your-api-key  # Optional
```

#### Data Management

- Node data is fetched from the external API
- Edit `assets/data/config.json` for site configuration
- Edit `assets/data/members.json` for member profiles
- Member avatars stored in `assets/images/avatars/`

#### File Structure
```
├── app/                      # Flask application package
│   ├── api_client.py        # External API client with caching
│   ├── data.py              # Data loading functions
│   └── routes/              # Blueprint modules
├── assets/
│   ├── css/                 # TailwindCSS files
│   ├── data/                # Static data (config.json, members.json)
│   ├── js/app.js            # Client-side JavaScript
│   └── images/              # Static assets
├── instance/cache/api/       # API response cache
├── templates/               # Jinja2 templates
└── requirements.txt         # Python dependencies
```

## Deployment

For traditional deployments:

```bash
# Install dependencies
pip install -r requirements.txt
npm install && npm run build-css-prod

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
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
4. Build CSS and test the application: `npm run build-css-prod && python app.py`
5. Commit changes: `git commit -am 'Add new feature'`
6. Push to branch: `git push origin feature/new-feature`
7. Create a Pull Request

## License

This project is open source and available under the [GPL-3.0 License](LICENSE).
