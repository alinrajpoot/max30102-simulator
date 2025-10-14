import socket
import threading
import json
import logging
import time
from typing import Dict, Any, Optional
from ..models.physiological_model import PhysiologicalModel
from .max30102_device import MAX30102Device
from .data_generator import DataGenerator

class TCPServer:
    """
    TCP Server for MAX30102 simulator that handles client connections
    and streams physiological data in real-time.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False
        self.lock = threading.Lock()
        
        # Initialize core components
        self.physio_model = PhysiologicalModel()
        self.max30102 = MAX30102Device()
        self.data_gen = DataGenerator(self.physio_model)
        
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging for the TCP server"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('TCPServer')
    
    def start_server(self):
        """Start the TCP server and begin accepting connections"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            
            self.running = True
            self.logger.info(f"MAX30102 Simulator TCP Server started on {self.host}:{self.port}")
            
            # Start client acceptance thread
            accept_thread = threading.Thread(target=self._accept_clients, daemon=True)
            accept_thread.start()
            
            # Start data broadcasting thread
            broadcast_thread = threading.Thread(target=self._broadcast_data, daemon=True)
            broadcast_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the TCP server and clean up resources"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        with self.lock:
            for client in self.clients:
                client.close()
            self.clients.clear()
        
        self.logger.info("TCP Server stopped")
    
    def _accept_clients(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.logger.info(f"New client connected: {client_address}")
                
                with self.lock:
                    self.clients.append(client_socket)
                
                # Send welcome message with current configuration
                welcome_msg = {
                    "type": "welcome",
                    "message": "Connected to MAX30102 Simulator",
                    "config": self.physio_model.get_current_state()
                }
                self._send_to_client(client_socket, welcome_msg)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error accepting client: {e}")
    
    def _broadcast_data(self):
        """Broadcast physiological data to all connected clients"""
        while self.running:
            try:
                if self.clients:
                    # Generate new data point
                    data_point = self.data_gen.generate_data_point()
                    
                    # Convert to JSON and send to all clients
                    data_json = json.dumps(data_point)
                    
                    with self.lock:
                        disconnected_clients = []
                        for client in self.clients:
                            try:
                                client.sendall((data_json + '\n').encode('utf-8'))
                            except (BrokenPipeError, ConnectionResetError, OSError):
                                disconnected_clients.append(client)
                        
                        # Remove disconnected clients
                        for client in disconnected_clients:
                            self.clients.remove(client)
                            client.close()
                            self.logger.info("Client disconnected")
                
                # Control data rate (adjust based on sample rate)
                time.sleep(0.001)  # ~1000 Hz
                
            except Exception as e:
                self.logger.error(f"Error broadcasting data: {e}")
                time.sleep(0.1)
    
    def _send_to_client(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Send a message to a specific client"""
        try:
            client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            self.logger.warning(f"Failed to send to client: {e}")
    
    def handle_client_message(self, client_socket: socket.socket, message: str):
        """
        Handle incoming messages from clients (configuration changes, commands, etc.)
        """
        try:
            data = json.loads(message.strip())
            command = data.get('command', '')
            
            self.logger.info(f"Received command: {command}")
            
            response = {"type": "command_response", "command": command, "success": True}
            
            if command == 'set_parameters':
                success = self.physio_model.update_parameters(data.get('parameters', {}))
                response['success'] = success
                if success:
                    response['new_state'] = self.physio_model.get_current_state()
            
            elif command == 'set_scenario':
                scenario = data.get('scenario', 'normal_resting')
                success = self.physio_model.set_scenario(scenario)
                response['success'] = success
                if success:
                    response['scenario'] = scenario
                    response['new_state'] = self.physio_model.get_current_state()
            
            elif command == 'get_status':
                response['status'] = {
                    'clients_connected': len(self.clients),
                    'model_state': self.physio_model.get_current_state(),
                    'sensor_status': self.max30102.get_status()
                }
            
            elif command == 'reset':
                self.physio_model.reset_to_defaults()
                response['new_state'] = self.physio_model.get_current_state()
            
            else:
                response['success'] = False
                response['error'] = f"Unknown command: {command}"
            
            self._send_to_client(client_socket, response)
            
        except json.JSONDecodeError as e:
            error_response = {
                "type": "error",
                "message": f"Invalid JSON: {e}"
            }
            self._send_to_client(client_socket, error_response)
        except Exception as e:
            error_response = {
                "type": "error", 
                "message": f"Error processing command: {e}"
            }
            self._send_to_client(client_socket, error_response)

def main():
    """Main entry point for the TCP server"""
    server = TCPServer()
    
    try:
        if server.start_server():
            print("Server is running. Press Ctrl+C to stop.")
            while server.running:
                time.sleep(1)
        else:
            print("Failed to start server")
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.stop_server()

if __name__ == "__main__":
    main()