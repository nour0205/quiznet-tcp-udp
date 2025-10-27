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

quiz_started = False  # Track if quiz has started

# Join the game
client_socket.sendto(f"join:{USERNAME}".encode(), ADDR)
print(f"{Colors.GREEN}✓ Connected to quiz server!{Colors.ENDC}")
print(f"{Colors.CYAN}Waiting for quiz to start...{Colors.ENDC}\n")

def listen():
    global quiz_started
    while True:
        try:
            msg, _ = client_socket.recvfrom(2048)
            msg = msg.decode()
            if msg.startswith("question:"):
                parts = msg.split(":", 2)
                qid = parts[1]
                question_data = parts[2].split("|")
                question_text = question_data[0]
                options = question_data[1:]
                
                print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}")
                print(f"📝 QUESTION {qid}")
                print(f"{'='*50}{Colors.ENDC}")
                print(f"{Colors.CYAN}{question_text}{Colors.ENDC}\n")
                
                # Display options vertically
                for option in options:
                    print(f"  {Colors.YELLOW}{option}{Colors.ENDC}")
                
                print(f"\n{Colors.YELLOW}⏱️  You have 10 seconds! Quick!{Colors.ENDC}\n")
            elif msg.startswith("broadcast:"):
                content = msg.split(':', 1)[1]
                if "correctly" in content.lower() and USERNAME in content:
                    print(f"{Colors.GREEN}{Colors.BOLD}✓ {content}{Colors.ENDC}")
                elif "incorrectly" in content.lower() and USERNAME in content:
                    print(f"{Colors.RED}{Colors.BOLD}✗ {content}{Colors.ENDC}")
                elif "joined" in content.lower():
                    print(f"{Colors.CYAN}👋 {content}{Colors.ENDC}")
                elif "starting" in content.lower():
                    quiz_started = True
                    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*50}")
                    print(f"🚀 {content}")
                    print(f"{'='*50}{Colors.ENDC}\n")
                elif "finished" in content.lower():
                    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
                    print(f"🏁 {content}")
                    print(f"{'='*50}{Colors.ENDC}\n")
                elif "time's up" in content.lower():
                    # Parse to make correct answer bold
                    # Format: "\n⏰ Time's up! Correct answer was X) Answer text."
                    if "correct answer was" in content.lower():
                        parts_split = content.split("Correct answer was ")
                        if len(parts_split) > 1:
                            before = parts_split[0]
                            answer_part = parts_split[1]
                            print(f"\n{Colors.YELLOW}{before}Correct answer was {Colors.BOLD}{answer_part}{Colors.ENDC}")
                        else:
                            print(f"\n{Colors.YELLOW}{content}{Colors.ENDC}")
                    else:
                        print(f"\n{Colors.YELLOW}{content}{Colors.ENDC}")
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
                print(f"{'='*50}{Colors.ENDC}\n")
                
                # Parse and display rankings vertically
                entries = ranking.split(" | ")
                medals = ["🥇", "🥈", "🥉"]
                for i, entry in enumerate(entries):
                    medal = medals[i] if i < 3 else "  "
                    # Extract place number and rest of entry
                    # Entry format: "1. username (score pts)"
                    print(f"{medal} {Colors.YELLOW}{entry}{Colors.ENDC}")
                print()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
            continue

# Run listener in background
threading.Thread(target=listen, daemon=True).start()

# Wait for quiz to start before showing input prompts
quiz_active = False

def wait_for_quiz_start():
    global quiz_active
    while not quiz_active:
        try:
            # Just sleep and wait
            import time
            time.sleep(0.5)
        except:
            break

# Don't show input prompt until quiz starts
import time as time_module
while not quiz_started:
    time_module.sleep(0.1)

# Send answers manually (only shows after quiz starts)
print(f"{Colors.BOLD}Type your answer (a/b/c) when questions appear, or 'quit' to exit.{Colors.ENDC}\n")

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
