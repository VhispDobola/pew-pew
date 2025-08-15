import socket
import json
import threading
from ursina import *

class NetworkManager(Entity):
    def __init__(self, is_host=False, host='localhost', port=5555):
        super().__init__()
        self.is_host = is_host
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients = {}
        self.running = False
        self.player_id = str(id(self))[-4:]  # Simple ID based on object id
        
        if is_host:
            self.socket.bind((host, port))
        else:
            self.socket.bind(('', 0))  # Bind to any available port for client
        
        self.socket.settimeout(0.1)  # Non-blocking mode with timeout
        
    def start(self):
        self.running = True
        threading.Thread(target=self._receive_thread, daemon=True).start()
        print(f"Network {'host' if self.is_host else 'client'} started on {self.host}:{self.port}")
    
    def stop(self):
        self.running = False
        self.socket.close()
    
    def _receive_thread(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                message = json.loads(data.decode())
                self._handle_message(message, addr)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Network error: {e}")
    
    def _handle_message(self, message, addr):
        message_type = message.get('type')
        
        if message_type == 'connect':
            self._handle_connect(message, addr)
        elif message_type == 'player_update':
            self._handle_player_update(message)
        elif message_type == 'shoot':
            self._handle_shoot(message)
        elif message_type == 'damage':
            self._handle_damage(message)
    
    def _handle_connect(self, message, addr):
        if not self.is_host:
            return
            
        player_id = message['player_id']
        self.clients[player_id] = addr
        print(f"Player {player_id} connected from {addr}")
        
        # Send current game state to the new player
        self.send_state_to_player(player_id)
    
    def _handle_player_update(self, message):
        # Update other players' positions
        player_id = message['player_id']
        position = message['position']
        rotation = message['rotation']
        
        # Update the corresponding player entity in the game
        if hasattr(self, 'on_player_update'):
            self.on_player_update(player_id, position, rotation)
    
    def _handle_shoot(self, message):
        # Handle bullet creation from other players
        if hasattr(self, 'on_shoot'):
            self.on_shoot(message)
    
    def _handle_damage(self, message):
        # Handle damage from other players
        if hasattr(self, 'on_damage'):
            self.on_damage(message)
    
    def send_connect(self):
        self.send_message({
            'type': 'connect',
            'player_id': self.player_id
        })
    
    def send_player_update(self, position, rotation):
        self.send_message({
            'type': 'player_update',
            'player_id': self.player_id,
            'position': position,
            'rotation': rotation
        })
    
    def send_shoot(self, position, direction):
        self.send_message({
            'type': 'shoot',
            'player_id': self.player_id,
            'position': position,
            'direction': direction
        })
    
    def send_damage(self, target_id, amount):
        self.send_message({
            'type': 'damage',
            'from_player': self.player_id,
            'target_id': target_id,
            'amount': amount
        })
    
    def send_message(self, message):
        try:
            if self.is_host:
                # Broadcast to all clients
                for client_id, addr in self.clients.items():
                    if client_id != message.get('player_id', ''):
                        self.socket.sendto(json.dumps(message).encode(), addr)
            else:
                # Send to host
                self.socket.sendto(json.dumps(message).encode(), (self.host, self.port))
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def send_state_to_player(self, player_id):
        if not self.is_host or not hasattr(self, 'get_game_state'):
            return
            
        state = self.get_game_state()
        message = {
            'type': 'game_state',
            'state': state
        }
        
        if player_id in self.clients:
            self.socket.sendto(json.dumps(message).encode(), self.clients[player_id])
