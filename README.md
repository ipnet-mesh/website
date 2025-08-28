# IPNet Community Website

[![Docker Build and Push](https://github.com/ipnet-mesh/website/actions/workflows/docker-build.yml/badge.svg)](https://github.com/ipnet-mesh/website/actions/workflows/docker-build.yml)

A Flask-based community website for IPNet (Ipswich Mesh Network), a local MeshCore community group serving Ipswich, Suffolk, UK. The site displays mesh network nodes, member profiles, and provides community information with interactive maps and statistics.

## Features

- **Interactive Node Map**: Geographic display of mesh network nodes with detailed information
- **Member Profiles**: Community member directory with avatars and contact preferences
- **Network Statistics**: Real-time coverage area calculations and network metrics
- **MQTT Integration**: Real-time data streaming from mesh network nodes
- **WebSocket API**: Live updates for node status, metrics, and network topology
- **Dark Mode Support**: User-configurable theme with persistent preferences
- **Mobile Responsive**: Optimized for all device sizes using TailwindCSS
- **Privacy Controls**: Configurable visibility for nodes and members


## Quick Start

## Architecture

### Backend (Flask)
- **app.py**: Main Flask application with routing and data management
- **Routes**: `/` (home), `/nodes/` (with optional area/node_id), `/members/`, `/contact/`, `/api/data`
- **Data Management**: JSON files from `assets/data/` directory with privacy filtering
- **WSGI Server**: Gunicorn for production deployments

### Frontend
- **Templates**: Jinja2 templates with inheritance from `templates/base.html`
- **Styling**: TailwindCSS with custom color scheme and dark mode
- **JavaScript**: Vanilla JS for data loading and client-side functionality
- **Alpine.js**: Lightweight reactivity for UI state management

### Data Structure
- **config.json**: Site configuration, contact info, theme settings
- **nodes.json**: Mesh network node data with locations, hardware specs, public keys
- **members.json**: Member profiles with avatars, bios, contact preferences

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+ (LTS)
- MQTT Broker (optional, for real-time features)

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

5. **Configure MQTT (optional)**
   ```bash
   # Set environment variables for MQTT broker connection
   export MQTT_BROKER_HOST=your-mqtt-broker.com
   export MQTT_USERNAME=your_username
   export MQTT_PASSWORD=your_password
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

#### Data Management

Edit JSON files in `assets/data/` directory:
- Use `isPublic: false` to hide sensitive nodes/members
- Node IDs follow format: `{shortname}.{area}.ipnt.uk`
- Member avatars stored in `assets/images/avatars/`
- Geographic coordinates required for coverage calculation

#### File Structure
```
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── package.json             # Node.js dependencies
├── tailwind.config.js       # TailwindCSS configuration
├── assets/
│   ├── css/
│   │   ├── input.css        # TailwindCSS source
│   │   └── output.css       # Generated CSS (do not edit)
│   ├── data/
│   │   ├── config.json      # Site configuration
│   │   ├── nodes.json       # Network nodes
│   │   └── members.json     # Community members
│   ├── js/
│   │   └── app.js          # Client-side JavaScript
│   └── images/             # Static assets
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Homepage
│   ├── nodes.html          # Nodes page
│   ├── members.html        # Members page
│   └── contact.html        # Contact page
└── CLAUDE.md               # Claude Code instructions
```

## MQTT and WebSocket Integration

The application supports real-time data streaming via MQTT broker connectivity with WebSocket API for live updates.

### Environment Variables

Configure MQTT connection using environment variables:

**Required:**
- `MQTT_BROKER_HOST` - MQTT broker hostname/IP address
- `MQTT_BROKER_PORT` - MQTT broker port (default: 1883)

**Connection Settings:**
- `MQTT_KEEPALIVE` - Keep-alive interval in seconds (default: 120)
- `MQTT_CLIENT_ID` - MQTT client ID (default: 'ipnet-website')

**Authentication (optional):**
- `MQTT_USERNAME` - MQTT username
- `MQTT_PASSWORD` - MQTT password

**TLS/SSL (optional):**
- `MQTT_USE_TLS` - Enable TLS (true/false, default: false)
- `MQTT_CA_CERT` - Path to CA certificate file
- `MQTT_CLIENT_CERT` - Path to client certificate file
- `MQTT_CLIENT_KEY` - Path to client private key file

### MQTT Topics

The application automatically subscribes to:
- `ipnet/+/status` - Node status updates (online/offline)
- `ipnet/+/metrics` - Node performance metrics
- `ipnet/network/topology` - Network topology changes
- `ipnet/alerts/+` - Alert messages from nodes

### Client-Side WebSocket API

```javascript
// Subscribe to additional topics
WebSocketAPI.subscribe('ipnet/custom/topic');

// Publish messages
WebSocketAPI.publish('ipnet/commands/restart', { node: 'ip2-rep01' });

// Get MQTT connection status
const status = WebSocketAPI.getMqttStatus();
```

### Real-time Features

- **Live Node Status**: Map markers update automatically when nodes go online/offline
- **Real-time Metrics**: Node performance data updates without page refresh
- **Network Topology**: Dynamic updates of network connections
- **Alert System**: Real-time notifications from mesh network nodes

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
