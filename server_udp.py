import socket
import time
import threading
from questions import QUESTIONS

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
quiz_started = False
questions = QUESTIONS

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
        opts = "|".join([f"{key}) {val}" for key, val in options.items()])
        broadcast(f"question:{qid}:{text}|{opts}")
        start = time.time()
        answered_users = set()  # Track who has answered this question

        while time.time() - start < 10:  # 10 sec limit for time-based scoring
            server_socket.settimeout(0.1)
            try:
                msg, addr = server_socket.recvfrom(1024)
                msg = msg.decode()
                if msg.startswith("answer:"):
                    _, username, choice = msg.split(":")
                    
                    # Check if user already answered this question
                    if username in answered_users:
                        continue
                    
                    answered_users.add(username)
                    
                    if choice == correct:
                        # Calculate time-based score (100 points max, decreases over 10 seconds)
                        elapsed = time.time() - start
                        points = max(10, int(100 - (elapsed * 9)))  # 100 to 10 points
                        scores[username] += points
                        broadcast(f"broadcast:{username} answered correctly! (+{points} points)")
                    else:
                        # Wrong answer = 0 points
                        broadcast(f"broadcast:{username} answered incorrectly. (0 points)")
            except socket.timeout:
                continue

        # Show correct answer if time's up
        broadcast(f"broadcast:\n⏰ Time's up! Correct answer was {correct}) {options[correct]}.")

        # Show scores
        score_msg = " ".join([f"{u}:{s}" for u, s in scores.items()])
        broadcast(f"score:{score_msg}")
        time.sleep(2)  # Brief pause between questions

    broadcast("broadcast:Quiz finished! Thanks for playing.")
    
    # Show final rankings
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ranking = " | ".join([f"{i+1}. {u} ({s} pts)" for i, (u, s) in enumerate(sorted_scores)])
    broadcast(f"ranking:{ranking}")
    print("[SERVER] Quiz ended.")
    print(f"Final Scores: {sorted_scores}")

# --- Main loop ---
def handle_messages():
    """Handle incoming client messages"""
    global quiz_started
    while not quiz_started:
        try:
            server_socket.settimeout(1)
            msg, addr = server_socket.recvfrom(1024)
            data = msg.decode()
            if data.startswith("join:"):
                handle_join(data, addr)
        except socket.timeout:
            continue

def server_console():
    """Handle server console commands"""
    global quiz_started
    while True:
        cmd = input()
        if cmd.lower() == "start":
            if len(clients) < 2:
                print("[ERROR] Need at least 2 players to start the quiz!")
                print(f"[INFO] Current players: {len(clients)}")
            elif not quiz_started:
                quiz_started = True
                print("[SERVER] Starting quiz...")
                broadcast("broadcast:Quiz is starting NOW! Get ready!")
                time.sleep(2)
                ask_questions()
                break
            else:
                print("[ERROR] Quiz already started!")
        elif cmd.lower() == "players":
            print(f"[INFO] Connected players ({len(clients)}): {', '.join(clients.keys())}")
        elif cmd.lower() == "help":
            print("[COMMANDS] start - Start the quiz (min 2 players)")
            print("[COMMANDS] players - Show connected players")
            print("[COMMANDS] help - Show this help message")

# Start message handler in background thread
print("\n[COMMANDS] Type 'start' to begin quiz (min 2 players)")
print("[COMMANDS] Type 'players' to see who's connected")
print("[COMMANDS] Type 'help' for all commands\n")

message_thread = threading.Thread(target=handle_messages, daemon=True)
message_thread.start()

# Run server console
server_console()
