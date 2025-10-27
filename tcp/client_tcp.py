import socket
import threading
import queue

class QuizClient:
    def __init__(self, server_ip, username):
        self.server_ip = server_ip
        self.username = username
        self.port = 8888
        self.socket = None
        self.connected = False
        self.message_queue = queue.Queue()
        self.listener_thread = None
        
    def connect(self):
        """Connect to the quiz server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.port))
            
            # Send join message
            self.socket.send(f"join:{self.username}".encode())
            self.connected = True
            
            # Start listener thread
            self.listener_thread = threading.Thread(target=self._listen, daemon=True)
            self.listener_thread.start()
            
            return True, "Connected successfully!"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def _listen(self):
        """Listen for messages from server"""
        while self.connected:
            try:
                msg = self.socket.recv(2048).decode()
                if not msg:
                    self.connected = False
                    break
                self.message_queue.put(msg)
            except Exception as e:
                self.connected = False
                break
    
    def send_answer(self, choice):
        """Send answer to server"""
        try:
            msg = f"answer:{self.username}:{choice}"
            self.socket.send(msg.encode())
            return True
        except:
            return False
    
    def get_message(self):
        """Get next message from queue (non-blocking)"""
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
