# 🧠 Knowledge Graph WebUI

Interactive web interface for visualizing and exploring the Thinking MCP memory graph.

## ✨ Features

- 📊 **Interactive Graph Visualization** - Visual network of entities and relationships
- 🔍 **Smart Search** - Search across entity names, types, and observations
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices
- 🎨 **Modern UI** - Beautiful gradients and smooth animations
- 🔄 **Real-time Data** - Live loading from memory.json
- 📈 **Statistics Dashboard** - Entity counts and type distribution

## 🚀 Quick Start

### 1. Start the WebUI Server

```bash
# Navigate to webui directory
cd webui

# Start the server (Python 3.6+)
python webui_server.py

# Or specify a custom port
python webui_server.py --port 8081
```

### 2. Open in Browser

Visit: **http://localhost:8080**

### 3. Explore Your Knowledge Graph

- 👆 **Click nodes** to see detailed information
- 🔍 **Search entities** using the search bar
- 📊 **View statistics** in the sidebar
- 🔄 **Refresh data** to see latest changes

## 🎯 API Endpoints

The WebUI server provides REST API endpoints:

### GET /api/memory
Returns all memory data (entities and relations)

```json
[
  {
    "type": "entity",
    "name": "Python",
    "entityType": "programming_language",
    "observations": ["High-level programming language", "..."]
  },
  {
    "type": "relation", 
    "from": "FastAPI",
    "to": "Python",
    "relationType": "built_with"
  }
]
```

### GET /api/stats
Returns graph statistics

```json
{
  "entities_count": 3,
  "relations_count": 2,
  "entity_types_count": 3,
  "entity_types": ["programming_language", "web_framework", "protocol"],
  "last_updated": 1623456789.123
}
```

## 🎨 Graph Visualization

### Node Colors
- 🟢 **Programming Language** - Green (#4CAF50)
- 🔵 **Web Framework** - Blue (#2196F3)  
- 🟠 **Protocol** - Orange (#FF9800)
- 🟣 **Database** - Purple (#9C27B0)
- 🔴 **Tool** - Red (#F44336)
- 🤎 **Concept** - Brown (#795548)
- ⚫ **Other** - Gray (#607D8B)

### Interactions
- **Click**: Select node and view details
- **Hover**: Highlight connections
- **Drag**: Reposition nodes
- **Zoom**: Mouse wheel or pinch gestures

## 📁 File Structure

```
webui/
├── index.html          # Main HTML page
├── style.css           # Styling and responsive design
├── app.js             # JavaScript application logic
├── webui_server.py    # Python web server with API
└── README.md          # This documentation
```

## 🔧 Requirements

- **Python 3.6+** for the web server
- **Modern Web Browser** with JavaScript enabled
- **Memory.json file** in `../app/memory.json`

## 🌐 Technology Stack

- **Frontend**: Vanilla JavaScript, CSS3, HTML5
- **Visualization**: Vis.js Network
- **Backend**: Python HTTP Server
- **Data Format**: JSON Lines (memory.json)

## 🐛 Troubleshooting

### Port Already in Use
```bash
python webui_server.py --port 8081
```

### Memory File Not Found
Ensure `memory.json` exists in the `app/` directory:
```
thinking-mcp/
├── app/
│   └── memory.json    # This file should exist
└── webui/
    └── webui_server.py
```

### Browser Compatibility
- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+

## 🎉 Usage Examples

### View Programming Languages
1. Search for "programming"
2. Click on Python node
3. See all observations and relationships

### Explore Frameworks
1. Look for blue nodes (web frameworks)
2. Click to see framework details
3. Follow edges to see dependencies

### Find Protocols
1. Search for "protocol"
2. Explore communication standards
3. See what uses each protocol

---

**🎯 Perfect for exploring your MCP server's knowledge graph visually!**
