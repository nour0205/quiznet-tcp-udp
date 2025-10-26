import socket
import time

# --- Server setup ---
HOST = "0.0.0.0"   # Listen on all interfaces
PORT = 8888
ADDR = (HOST, PORT)

# Create UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(ADDR)

print(f"[SERVER STARTED] Listening on UDP port {PORT} ...")

clients = {}  # username -> address
scores = {}   # username -> score

# Example quiz questions
questions = [
    ("What does TCP stand for?", "b", {"a": "Transfer Control Packet", "b": "Transmission Control Protocol", "c": "Transport Connection Port"}),
    ("Which protocol is connectionless?", "a", {"a": "UDP", "b": "TCP", "c": "HTTP"}),
    ("Port number for HTTP?", "c", {"a": "20", "b": "25", "c": "80"}),
]

def broadcast(message):
    for addr in clients.values():
        server_socket.sendto(message.encode(), addr)

def handle_join(data, addr):
    username = data.split(":", 1)[1]
    clients[username] = addr
    scores[username] = 0
    print(f"[JOIN] {username} joined from {addr}")
    broadcast(f"broadcast:{username} joined the quiz!")

def ask_questions():
    for qid, (text, correct, options) in enumerate(questions, 1):
        print(f"[QUESTION {qid}] Broadcasting...")
        opts = " ".join([f"{key}) {val}" for key, val in options.items()])
        broadcast(f"question:{qid}:{text} [{opts}]")
        start = time.time()
        answered = False
        winner = None

        while time.time() - start < 20:  # 20 s limit
            server_socket.settimeout(1)
            try:
                msg, addr = server_socket.recvfrom(1024)
                msg = msg.decode()
                if msg.startswith("answer:"):
                    _, username, choice = msg.split(":")
                    if not answered and choice == correct:
                        scores[username] += 1
                        broadcast(f"broadcast:{username} answered correctly first!")
                        answered = True
                        winner = username
                    elif not answered:
                        server_socket.sendto("broadcast:Wrong answer.".encode(), addr)
            except socket.timeout:
                continue

        if not answered:
            broadcast(f"broadcast:Time's up! Correct answer was {correct}) {options[correct]}.")

        # Show scores
        score_msg = " ".join([f"{u}:{s}" for u, s in scores.items()])
        broadcast(f"score:{score_msg}")

    broadcast("broadcast:Quiz finished! Thanks for playing.")
    print("[SERVER] Quiz ended.")

# --- Main loop ---
while True:
    msg, addr = server_socket.recvfrom(1024)
    data = msg.decode()
    if data.startswith("join:"):
        handle_join(data, addr)
        if len(clients) >= 2:  # start when 2 players joined (adjust as needed)
            broadcast("broadcast:Starting quiz in 5 seconds...")
            time.sleep(5)
            ask_questions()
            break
