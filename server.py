"""Simple HTTP server for Render health checks"""
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple health check endpoint"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK - LinkedIn Automation Running')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")


def start_health_server(port=None):
    """Start health check server in background thread"""
    if port is None:
        port = int(os.environ.get('PORT', 10000))

    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)

    def run_server():
        logger.info(f"Health check server started on port {port}")
        server.serve_forever()

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    logger.info("Health check server thread started")
    return server
