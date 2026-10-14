#!/usr/bin/env python3
import http.server
import ssl
import socketserver
import os
import sys

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

PORT = 8181
Handler = MyHTTPRequestHandler

# Check if SSL files exist
if not os.path.exists('ssl/server.pem') or not os.path.exists('ssl/server.key'):
    print("❌ SSL certificate files not found!")
    print("   Make sure ssl/server.pem and ssl/server.key exist")
    sys.exit(1)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('ssl/server.pem', 'ssl/server.key')
    
    # Wrap the socket with SSL
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print(f"✅ HTTPS Server running on https://localhost:{PORT}")
    print("📁 Serving files from current directory")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()
