#!/usr/bin/env python3
"""
Simple web server for Knowledge Graph WebUI
Serves static files and provides API endpoint for memory.json data
"""

import json
import os
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from pathlib import Path

class MemoryAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        self.webui_dir = Path(__file__).parent
        self.memory_file = self.webui_dir.parent / "app" / "memory.json"
        super().__init__(*args, directory=str(self.webui_dir), **kwargs)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        # API endpoint for memory data
        if parsed_url.path == '/api/memory':
            self.serve_memory_data()
        # API endpoint for graph statistics
        elif parsed_url.path == '/api/stats':
            self.serve_stats()
        # Serve static files
        else:
            super().do_GET()

    def serve_memory_data(self):
        """Serve memory.json data as JSON API"""
        try:
            if self.memory_file.exists():
                memory_data = []
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            memory_data.append(json.loads(line))
                
                self.send_json_response(memory_data)
            else:
                self.send_json_response([], 404, "Memory file not found")
                
        except Exception as e:
            self.send_json_response(
                {"error": str(e)}, 
                500, 
                "Error reading memory data"
            )

    def serve_stats(self):
        """Serve graph statistics"""
        try:
            if self.memory_file.exists():
                entities = []
                relations = []
                
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            if data.get('type') == 'entity':
                                entities.append(data)
                            elif data.get('type') == 'relation':
                                relations.append(data)
                
                entity_types = set(e.get('entityType', 'unknown') for e in entities)
                
                stats = {
                    "entities_count": len(entities),
                    "relations_count": len(relations),
                    "entity_types_count": len(entity_types),
                    "entity_types": list(entity_types),
                    "last_updated": os.path.getmtime(self.memory_file) if self.memory_file.exists() else None
                }
                
                self.send_json_response(stats)
            else:
                self.send_json_response({
                    "entities_count": 0,
                    "relations_count": 0,
                    "entity_types_count": 0,
                    "entity_types": [],
                    "last_updated": None
                })
                
        except Exception as e:
            self.send_json_response(
                {"error": str(e)}, 
                500, 
                "Error getting statistics"
            )

    def send_json_response(self, data, status_code=200, status_message="OK"):
        """Send JSON response with proper headers"""
        self.send_response(status_code, status_message)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Custom log message format"""
        print(f"[WebUI] {format % args}")

def start_server(port=8080):
    """Start the web server"""
    try:
        with socketserver.TCPServer(("", port), MemoryAPIHandler) as httpd:
            print(f"🌐 Knowledge Graph WebUI Server started!")
            print(f"📊 Dashboard: http://localhost:{port}")
            print(f"🔗 Memory API: http://localhost:{port}/api/memory")
            print(f"📈 Stats API: http://localhost:{port}/api/stats")
            print(f"🛑 Press Ctrl+C to stop the server\n")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            print(f"❌ Port {port} is already in use. Try a different port.")
            print(f"💡 Example: python webui_server.py --port 8081")
        else:
            print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Knowledge Graph WebUI Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on (default: 8080)")
    
    args = parser.parse_args()
    start_server(args.port)
