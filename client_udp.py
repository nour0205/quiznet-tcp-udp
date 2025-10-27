import socket
import threading
import sys

# ANSI Color codes for terminal styling
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════╗
║        🎯 QUIZNET UDP QUIZ 🎯         ║
║     Real-time Multiplayer Quiz!       ║
╚═══════════════════════════════════════╝
{Colors.ENDC}"""
    print(banner)

print_banner()

SERVER_IP = input(f"{Colors.YELLOW}Enter server IP: {Colors.ENDC}")
USERNAME = input(f"{Colors.YELLOW}Enter your username: {Colors.ENDC}")

ADDR = (SERVER_IP, 8888)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(0.5)

# Join the game
client_socket.sendto(f"join:{USERNAME}".encode(), ADDR)
print(f"{Colors.GREEN}✓ Connected to quiz server!{Colors.ENDC}")
print(f"{Colors.CYAN}Waiting for quiz to start...{Colors.ENDC}\n")

def listen():
    while True:
        try:
            msg, _ = client_socket.recvfrom(2048)
            msg = msg.decode()
            if msg.startswith("question:"):
                parts = msg.split(":", 2)
                qid = parts[1]
                question = parts[2]
                print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}")
                print(f"📝 QUESTION {qid}")
                print(f"{'='*50}{Colors.ENDC}")
                print(f"{Colors.CYAN}{question}{Colors.ENDC}")
                print(f"{Colors.YELLOW}⏱️  You have 10 seconds! Quick!{Colors.ENDC}\n")
            elif msg.startswith("broadcast:"):
                content = msg.split(':', 1)[1]
                if "correct" in content.lower() and USERNAME in content:
                    print(f"{Colors.GREEN}{Colors.BOLD}✓ {content}{Colors.ENDC}")
                elif "incorrect" in content.lower() and USERNAME in content:
                    print(f"{Colors.RED}{Colors.BOLD}✗ {content}{Colors.ENDC}")
                elif "joined" in content.lower():
                    print(f"{Colors.CYAN}👋 {content}{Colors.ENDC}")
                elif "starting" in content.lower():
                    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*50}")
                    print(f"🚀 {content}")
                    print(f"{'='*50}{Colors.ENDC}\n")
                elif "finished" in content.lower():
                    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
                    print(f"🏁 {content}")
                    print(f"{'='*50}{Colors.ENDC}\n")
                elif "time's up" in content.lower():
                    print(f"{Colors.RED}⏰ {content}{Colors.ENDC}")
                else:
                    print(f"{Colors.YELLOW}📢 {content}{Colors.ENDC}")
            elif msg.startswith("score:"):
                scores = msg.split(':', 1)[1]
                print(f"\n{Colors.BOLD}{Colors.HEADER}📊 CURRENT SCORES:{Colors.ENDC}")
                for entry in scores.split():
                    user, score = entry.split(":")
                    color = Colors.GREEN if user == USERNAME else Colors.CYAN
                    marker = "👉 " if user == USERNAME else "   "
                    print(f"{marker}{color}{user}: {score} points{Colors.ENDC}")
                print()
            elif msg.startswith("ranking:"):
                ranking = msg.split(':', 1)[1]
                print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*50}")
                print(f"🏆 FINAL RANKINGS 🏆")
                print(f"{'='*50}{Colors.ENDC}")
                print(f"{Colors.YELLOW}{ranking}{Colors.ENDC}\n")
        except socket.timeout:
            continue
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
            continue

# Run listener in background
threading.Thread(target=listen, daemon=True).start()

# Send answers manually
print(f"{Colors.BOLD}Ready to play! Type your answer (a/b/c) when questions appear.{Colors.ENDC}")
print(f"{Colors.BOLD}Type 'quit' to exit.{Colors.ENDC}\n")

while True:
    try:
        choice = input(f"{Colors.BOLD}Your answer ➤ {Colors.ENDC}").strip().lower()
        if choice == "quit":
            print(f"{Colors.YELLOW}Goodbye! Thanks for playing!{Colors.ENDC}")
            break
        if choice in ["a", "b", "c"]:
            msg = f"answer:{USERNAME}:{choice}"
            client_socket.sendto(msg.encode(), ADDR)
            print(f"{Colors.GREEN}✓ Answer sent!{Colors.ENDC}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Goodbye! Thanks for playing!{Colors.ENDC}")
        break
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        continue
