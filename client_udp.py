import socket
import threading

SERVER_IP = input("Enter server IP: ")
USERNAME = input("Enter your username: ")

ADDR = (SERVER_IP, 8888)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(0.5)

# Join the game
client_socket.sendto(f"join:{USERNAME}".encode(), ADDR)

def listen():
    while True:
        try:
            msg, _ = client_socket.recvfrom(2048)
            msg = msg.decode()
            if msg.startswith("question:"):
                parts = msg.split(":", 2)
                print(f"\n {parts[2]}")
            elif msg.startswith("broadcast:"):
                print(f"\n {msg.split(':',1)[1]}")
            elif msg.startswith("score:"):
                print(f"\n Scores → {msg.split(':',1)[1]}")
        except socket.timeout:
            continue

# Run listener in background
threading.Thread(target=listen, daemon=True).start()

# Send answers manually
while True:
    choice = input("Your answer (a/b/c or 'quit'): ").strip().lower()
    if choice == "quit":
        break
    if choice in ["a", "b", "c"]:
        msg = f"answer:{USERNAME}:{choice}"
        client_socket.sendto(msg.encode(), ADDR)
