#!/usr/bin/env python
import BaseHTTPServer
import SimpleHTTPServer
import ssl
import os
import sys

PORT = 8181
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

# Check if SSL files exist
if not os.path.exists('ssl/server.pem') or not os.path.exists('ssl/server.key'):
    print("❌ SSL certificate files not found!")
    print("   Make sure ssl/server.pem and ssl/server.key exist")
    sys.exit(1)

httpd = BaseHTTPServer.HTTPServer(('localhost', PORT), Handler)
httpd.socket = ssl.wrap_socket(httpd.socket, 
                               certfile='ssl/server.pem', 
                               keyfile='ssl/server.key', 
                               server_side=True)

print("✅ HTTPS Server running on https://localhost:%d" % PORT)
print("📁 Serving files from current directory")
print("🛑 Press Ctrl+C to stop")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\n🛑 Server stopped")
    httpd.shutdown()
