#!/bin/bash

# SSL HTTPS Server Setup Script
# Creates SSL certificates and serves HTML files on port 8181

set -e  # Exit on any error

PORT=8181
SSL_DIR="ssl"
SERVER_NAME="localhost"

echo "🔒 Setting up HTTPS server on port $PORT..."

# Create SSL directory if it doesn't exist
if [ ! -d "$SSL_DIR" ]; then
    echo "📁 Creating SSL directory..."
    mkdir -p "$SSL_DIR"
fi

# Generate SSL certificate and key if they don't exist
if [ ! -f "$SSL_DIR/server.key" ] || [ ! -f "$SSL_DIR/server.pem" ]; then
    echo "🔑 Generating SSL certificate and key..."
    
    # Generate private key
    openssl genrsa -out "$SSL_DIR/server.key" 2048
    
    # Generate self-signed certificate
    openssl req -new -x509 -key "$SSL_DIR/server.key" -out "$SSL_DIR/server.pem" -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=$SERVER_NAME"
    
    echo "✅ SSL certificate generated successfully!"
    echo "   Key: $SSL_DIR/server.key"
    echo "   Certificate: $SSL_DIR/server.pem"
else
    echo "✅ SSL certificate already exists"
fi

# Create a sample index.html if it doesn't exist
if [ ! -f "index.html" ]; then
    echo "📄 Creating sample index.html..."
    cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure HTTPS Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .success {
            color: #27ae60;
            border: 2px solid #27ae60;
            background: #d5f4e6;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .info {
            color: #2980b9;
            background: #ebf3fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Secure HTTPS Server</h1>
        
        <div class="success">
            <strong>✅ Success!</strong> Your HTTPS server is running securely on port 8181.
        </div>
        
        <div class="info">
            <strong>ℹ️ Note:</strong> This server is using a self-signed certificate. 
            Your browser may show a security warning - this is normal for development.
        </div>
        
        <h2>Server Details:</h2>
        <ul>
            <li><strong>Port:</strong> 8181</li>
            <li><strong>Protocol:</strong> HTTPS</li>
            <li><strong>Certificate:</strong> Self-signed</li>
            <li><strong>Current Time:</strong> <span id="time"></span></li>
        </ul>
        
        <h2>Files in Directory:</h2>
        <p>Place your HTML files in this directory to serve them securely.</p>
    </div>
    
    <script>
        // Update time every second
        function updateTime() {
            document.getElementById('time').textContent = new Date().toLocaleString();
        }
        updateTime();
        setInterval(updateTime, 1000);
    </script>
</body>
</html>
EOF
    echo "✅ Sample index.html created"
fi

# Check if Python is available and start appropriate server
if command -v python3 &> /dev/null; then
    echo "🚀 Starting HTTPS server with Python 3..."
    echo "   URL: https://localhost:$PORT"
    echo "   Press Ctrl+C to stop the server"
    echo ""
    
    python3 << EOF
import http.server
import ssl
import socketserver
import os

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

PORT = $PORT
Handler = MyHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('$SSL_DIR/server.pem', '$SSL_DIR/server.key')
    
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
EOF

elif command -v python &> /dev/null; then
    echo "🚀 Starting HTTPS server with Python 2..."
    echo "   URL: https://localhost:$PORT"
    echo "   Press Ctrl+C to stop the server"
    echo ""
    
    python << EOF
import BaseHTTPServer
import SimpleHTTPServer
import ssl
import os

PORT = $PORT
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = BaseHTTPServer.HTTPServer(('localhost', PORT), Handler)
httpd.socket = ssl.wrap_socket(httpd.socket, 
                               certfile='$SSL_DIR/server.pem', 
                               keyfile='$SSL_DIR/server.key', 
                               server_side=True)

print("✅ HTTPS Server running on https://localhost:%d" % PORT)
print("📁 Serving files from current directory")
print("🛑 Press Ctrl+C to stop")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\n🛑 Server stopped")
    httpd.shutdown()
EOF

else
    echo "❌ Python not found. Please install Python to run this server."
    exit 1
fi
