# Just a simple healthceck server :P
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Define the endpoint for health check
        if self.path == "/health":
            self.send_response(200)  # Send HTTP 200 status
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Server is healthy!")
        else:
            self.send_response(404)  # Send HTTP 404 for other paths
            self.end_headers()

# Configure the server
host = "0.0.0.0"
port = int(os.environ.get('PORT'))
server = HTTPServer((host, port), HealthCheckHandler)

print(f"Health check server running on http://{host}:{port}/health")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down server...")
    server.server_close()

