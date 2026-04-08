#!/usr/bin/env python3
"""
Simple HTTP server for OmniAudit Environment
Uses Python's built-in http.server to avoid compatibility issues
"""

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

# Add parent directory to path to import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Action, ActionType
from env import OmniAuditEnvironment

# Global environment instance
env = OmniAuditEnvironment()

class OmniAuditHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json(self, data, status_code=200):
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def _send_error(self, message, status_code=500):
        self._send_json({"error": message}, status_code)

    def do_OPTIONS(self):
        """Handle preflight requests"""
        self._set_headers(204)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        try:
            if parsed_path.path == '/':
                self._send_json({
                    "message": "OmniAudit Environment API",
                    "version": "1.0.0",
                    "status": "running",
                    "endpoints": [
                        "/reset",
                        "/step", 
                        "/state",
                        "/tasks",
                        "/grader"
                    ]
                })
            
            elif parsed_path.path == '/state':
                self._send_json(env.get_state().model_dump())
            
            elif parsed_path.path == '/tasks':
                tasks = env.get_tasks()
                task_dict = {task.name.lower().replace(" ", "_"): task.model_dump() for task in tasks}
                self._send_json(task_dict)
            
            elif parsed_path.path == '/grader':
                grade = env.grade()
                state = env.get_state()
                self._send_json({
                    "grade": grade,
                    "is_complete": state.is_complete,
                    "tasks_completed": state.tasks_completed,
                    "total_steps": state.step_count,
                    "total_reward": state.total_reward
                })
            
            elif parsed_path.path == '/health':
                self._send_json({"status": "healthy", "environment": "OmniAudit"})
            
            else:
                self._send_error("Endpoint not found", 404)
        
        except Exception as e:
            self._send_error(f"Request failed: {str(e)}")

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        content_length = int(self.headers['Content-Length']) if 'Content-Length' in self.headers else 0
        
        try:
            action_data = {}
            if content_length > 0:
                post_data = self.rfile.read(content_length).decode('utf-8')
                if post_data.strip():
                    action_data = json.loads(post_data)
            
            if parsed_path.path == '/reset':
                observation = env.reset()
                self._send_json(observation.model_dump())
            
            elif parsed_path.path == '/step':
                # Convert dict to Action dataclass
                action = Action(
                    cmd=ActionType(action_data.get("cmd")),
                    target_id=action_data.get("target_id"),
                    key=action_data.get("key"),
                    value=action_data.get("value")
                )
                
                observation, reward, done, info = env.step(action)
                state = info["state"]
                
                self._send_json({
                    "observation": observation.model_dump(),
                    "reward": reward.model_dump(),
                    "done": done,
                    "state": state
                })
            
            else:
                self._send_error("Endpoint not found", 404)
        
        except json.JSONDecodeError:
            self._send_error("Invalid JSON in request body", 400)
        except Exception as e:
            self._send_error(f"Request failed: {str(e)}")

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def main():
    """Start HTTP server"""
    server_address = ('0.0.0.0', 7860)
    httpd = HTTPServer(server_address, OmniAuditHandler)
    
    print("Starting OmniAudit Environment Server...")
    print("Available endpoints:")
    print("  GET  /           - API info")
    print("  POST /reset      - Reset environment")
    print("  POST /step       - Execute action")
    print("  GET  /state      - Get current state")
    print("  GET  /tasks      - Get task information")
    print("  GET  /grader     - Get grade")
    print("  GET  /health     - Health check")
    print()
    print("Server running on http://localhost:7860")
    print("Press Ctrl+C to stop server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    main()
