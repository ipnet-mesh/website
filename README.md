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

## Example: MeshCore Integration

This website is part of the IPNet mesh network ecosystem. Here's an example of interacting with a mesh node using Claude with the MeshCore MCP server:

<div align="center">

```markdown
┌─────────────────────────────────────────────────────────────────────┐
│ 💬 Conversation with Claude via OpenWebUI + MeshCore MCP Server    │
└─────────────────────────────────────────────────────────────────────┘
```

</div>

> **👤 USER**
> Are you connected to MeshCore?

> **🤖 CLAUDE**
> Yes, I am connected to MeshCore. I can see the device information showing a **Heltec V3** device running firmware version **8 (v1.10.0-9405e8b)** built on November 13, 2025. The device supports up to **350 contacts** and **40 channels**.

---

> **👤 USER**
> Do I have any messages?

> **🤖 CLAUDE**
> No, you don't have any messages. Your message buffer is currently empty.

---

> **👤 USER**
> Someone has sent a message. Can you check again?

> **🤖 CLAUDE**
> You're right! You do have a message now. There's **1 message** in your buffer:
>
> **Message Details:**
> - **From:** Unknown (Public Key: `2369759a4926`)
> - **Time:** November 22, 2025 at 13:46:24
> - **Message:** *"Hello GitHub!"*
>
> It appears to be from an unknown contact, but you can see their public key identifier.

---

> **👤 USER**
> Reply to that message saying "Hello World!"

> **🤖 CLAUDE**
> I've successfully sent your reply! The message **"Hello World!"** has been sent to contact `2369759a4926`. The system confirms the message was sent successfully. ✓

<div align="center">

```markdown
┌─────────────────────────────────────────────────────────────────────┐
│ This demonstrates Claude's ability to interact with mesh network    │
│ nodes through the MeshCore MCP server, enabling message reading,    │
│ sending, and device management through natural language.            │
└─────────────────────────────────────────────────────────────────────┘
```

</div>

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
