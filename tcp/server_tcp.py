import socket
import time
import threading
import sys
import os

# Add parent directory to path to import questions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from questions import QUESTIONS

# --- Server setup ---
HOST = "0.0.0.0"   # Listen on all interfaces
PORT = 8888
ADDR = (HOST, PORT)

# Create TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(ADDR)
server_socket.listen()

print(f"[SERVER STARTED] Listening on TCP port {PORT} ...")

clients = {}  # username -> connection object
scores = {}   # username -> score
answer_queues = {}  # username -> queue of answers
quiz_started = False
questions = QUESTIONS
clients_lock = threading.Lock()

def broadcast(message):
    """Send message to all connected clients"""
    with clients_lock:
        disconnected = []
        for username, conn in clients.items():
            try:
                conn.send(message.encode())
            except:
                disconnected.append(username)
        
        # Remove disconnected clients
        for username in disconnected:
            print(f"[DISCONNECT] {username} disconnected")
            del clients[username]
            if username in scores:
                del scores[username]

def handle_client(conn, addr):
    """Handle individual client connection"""
    username = None
    try:
        # First message should be join with username
        data = conn.recv(1024).decode()
        if data.startswith("join:"):
            username = data.split(":", 1)[1]
            with clients_lock:
                clients[username] = conn
                scores[username] = 0
                answer_queues[username] = []
            print(f"[JOIN] {username} joined from {addr}")
            broadcast(f"broadcast:{username} joined the quiz!")
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                conn.settimeout(1.0)
                msg = conn.recv(1024).decode()
                if not msg:
                    break
                
                # Store answer messages in queue for ask_questions to process
                if msg.startswith("answer:"):
                    with clients_lock:
                        if username in answer_queues:
                            answer_queues[username].append(msg)
            except socket.timeout:
                continue
            except:
                break
    except Exception as e:
        print(f"[ERROR] Client handler error: {e}")
    finally:
        if username:
            with clients_lock:
                if username in clients:
                    del clients[username]
                if username in scores:
                    del scores[username]
                if username in answer_queues:
                    del answer_queues[username]
            print(f"[DISCONNECT] {username} disconnected")

def accept_connections():
    """Accept new client connections"""
    global quiz_started
    while not quiz_started:
        try:
            server_socket.settimeout(1)
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[ERROR] Accept error: {e}")

def ask_questions():
    """Run the quiz by broadcasting questions and collecting answers"""
    for qid, (text, correct, options) in enumerate(questions, 1):
        print(f"[QUESTION {qid}] Broadcasting...")
        opts = "|".join([f"{key}) {val}" for key, val in options.items()])
        broadcast(f"question:{qid}:{text}|{opts}")
        
        start = time.time()
        answered_users = set()  # Track who has answered this question

        while time.time() - start < 10:  # 10 sec limit
            time.sleep(0.1)  # Small delay to prevent busy-waiting
            
            with clients_lock:
                # Check answer queues for all users
                for username in list(answer_queues.keys()):
                    if username in answered_users:
                        continue
                    
                    # Check if this user has submitted an answer
                    if answer_queues[username]:
                        msg = answer_queues[username].pop(0)
                        
                        if msg.startswith("answer:"):
                            _, user, choice = msg.split(":")
                            if user == username and user not in answered_users:
                                answered_users.add(user)
                                
                                if choice == correct:
                                    # Calculate time-based score
                                    elapsed = time.time() - start
                                    points = max(10, int(100 - (elapsed * 9)))
                                    scores[username] += points
                                    broadcast(f"broadcast:{username} answered correctly! (+{points} points)")
                                else:
                                    broadcast(f"broadcast:{username} answered incorrectly. (0 points)")

        # Show correct answer
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

# Start connection acceptor in background
print("\n[COMMANDS] Type 'start' to begin quiz (min 2 players)")
print("[COMMANDS] Type 'players' to see who's connected")
print("[COMMANDS] Type 'help' for all commands\n")

accept_thread = threading.Thread(target=accept_connections, daemon=True)
accept_thread.start()

# Run server console
server_console()
