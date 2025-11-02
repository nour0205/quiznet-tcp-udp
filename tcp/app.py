import streamlit as st
import sys
import os
import time

# Add tcp directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tcp'))
from client_tcp import QuizClient

# Page config
st.set_page_config(
    page_title="QuizNet TCP Quiz",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Kahoot-inspired CSS
st.markdown("""
    <style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0 !important;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Custom header - compact */
    .quiz-header {
        text-align: center;
        color: white;
        font-size: 2.5em;
        font-weight: 900;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        margin: 10px 0;
        letter-spacing: 2px;
    }
    
    .quiz-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.9);
        font-size: 1em;
        margin-bottom: 15px;
    }
    
    /* Question box - Kahoot style - compact */
    .question-container {
        background: rgba(0, 0, 0, 0.7);
        border-radius: 15px;
        padding: 20px;
        margin: 10px auto;
        max-width: 800px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        text-align: center;
    }
    
    .question-number {
        color: #FFD700;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .question-text {
        color: white !important;
        font-size: 1.6em;
        font-weight: 700;
        margin: 10px 0;
        line-height: 1.3;
    }
    
    /* Timer bar - compact */
    .timer-container {
        margin: 10px auto;
        max-width: 800px;
    }
    
    /* Answer buttons - Kahoot colors - smaller */
    div.stButton > button {
        width: 100%;
        height: 80px;
        font-size: 1.1em;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    
    /* Kahoot button colors */
    [data-testid="column"]:nth-of-type(1) button {
        background: linear-gradient(135deg, #E21B3C 0%, #D01257 100%);
    }
    
    [data-testid="column"]:nth-of-type(2) button {
        background: linear-gradient(135deg, #1368CE 0%, #0D5EB9 100%);
    }
    
    [data-testid="column"]:nth-of-type(3) button {
        background: linear-gradient(135deg, #D89E00 0%, #C78900 100%);
    }
    
    [data-testid="column"]:nth-of-type(4) button {
        background: linear-gradient(135deg, #26890C 0%, #1F6F0A 100%);
    }
    
    /* Score board - compact */
    .score-board {
        background: rgba(255,255,255,0.95);
        border-radius: 12px;
        padding: 15px;
        margin: 10px auto;
        max-width: 500px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .score-title {
        color: #46178F;
        font-size: 1.4em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }
    
    .score-entry {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 10px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 1em;
        font-weight: 600;
        color: #333;
    }
    
    .score-entry.current-user {
        background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
        color: white;
        transform: scale(1.05);
    }
    
    /* Connection box - smaller button */
    .connection-box {
        background: white;
        border-radius: 15px;
        padding: 30px;
        margin: 30px auto;
        max-width: 400px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    
    /* Join button - normal size */
    .stButton > button[kind="primary"] {
        height: 45px !important;
        font-size: 1.1em !important;
    }
    
    /* Status messages - compact */
    .status-waiting {
        background: rgba(255,255,255,0.95);
        border-radius: 12px;
        padding: 20px;
        margin: 15px auto;
        max-width: 500px;
        text-align: center;
        font-size: 1.1em;
        color: #46178F;
        font-weight: 600;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Ranking podium - compact */
    .ranking-container {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px auto;
        max-width: 600px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    
    .ranking-title {
        text-align: center;
        color: #46178F;
        font-size: 2em;
        font-weight: 900;
        margin-bottom: 20px;
    }
    
    .rank-entry {
        padding: 12px;
        margin: 10px 0;
        border-radius: 10px;
        font-size: 1.1em;
        font-weight: 700;
        text-align: center;
    }
    
    .rank-1 {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: white;
        font-size: 1.3em;
    }
    
    .rank-2 {
        background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%);
        color: white;
    }
    
    .rank-3 {
        background: linear-gradient(135deg, #CD7F32 0%, #B8732D 100%);
        color: white;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #ddd;
        padding: 10px;
        font-size: 1em;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #46178F;
        height: 12px;
        border-radius: 10px;
    }
    
    /* Sidebar compact */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.8);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'client' not in st.session_state:
    st.session_state.client = None
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'scores' not in st.session_state:
    st.session_state.scores = {}
if 'ranking' not in st.session_state:
    st.session_state.ranking = None
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'answer_sent' not in st.session_state:
    st.session_state.answer_sent = False

# Header
st.markdown('<div class="quiz-header">🎯 QUIZNET TCP QUIZ 🎯</div>', unsafe_allow_html=True)
st.markdown('<p class="quiz-subtitle">Real-time Multiplayer Quiz!</p>', unsafe_allow_html=True)

# Connection section
if not st.session_state.connected:
    st.markdown('<div class="connection-box">', unsafe_allow_html=True)
    st.markdown("### 📡 Join the Quiz")
    
    server_ip = st.text_input("Server IP", value="127.0.0.1", placeholder="Enter server IP address")
    username = st.text_input("Username", value="", placeholder="Choose your username")
    
    if st.button("🚀 JOIN GAME", type="primary", use_container_width=True):
        if username.strip():
            client = QuizClient(server_ip, username)
            success, msg = client.connect()
            
            if success:
                st.session_state.client = client
                st.session_state.connected = True
                st.session_state.messages.append(("success", "✓ Connected to quiz server!"))
                st.rerun()
            else:
                st.error(f"❌ {msg}")
        else:
            st.warning("Please enter a username!")
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Connected - show quiz interface
    
    # Process ALL incoming messages (check multiple times to catch everything)
    if st.session_state.client:
        messages_processed = 0
        max_messages = 50  # Process up to 50 messages per rerun
        
        while messages_processed < max_messages:
            msg = st.session_state.client.get_message()
            if not msg:
                break
            
            messages_processed += 1
                
            if msg.startswith("question:"):
                parts = msg.split(":", 2)
                qid = parts[1]
                question_data = parts[2].split("|")
                question_text = question_data[0]
                options = question_data[1:]
                
                st.session_state.current_question = {
                    'id': qid,
                    'text': question_text,
                    'options': options,
                    'start_time': time.time()
                }
                st.session_state.answer_sent = False
                st.session_state.quiz_started = True
                
            elif msg.startswith("broadcast:"):
                content = msg.split(':', 1)[1]
                st.session_state.messages.append(("broadcast", content))
                
            elif msg.startswith("score:"):
                scores = msg.split(':', 1)[1]
                st.session_state.scores = {}
                for entry in scores.split():
                    if ':' in entry:
                        user, score = entry.split(":")
                        st.session_state.scores[user] = int(score)
                        
            elif msg.startswith("ranking:"):
                ranking = msg.split(':', 1)[1]
                st.session_state.ranking = ranking
                st.session_state.current_question = None
    
    # Show current question
    if st.session_state.current_question and not st.session_state.answer_sent:
        q = st.session_state.current_question
        
        # Question container
        st.markdown('<div class="question-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="question-number">Question {q["id"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="question-text">{q["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Timer
        elapsed = time.time() - q['start_time']
        remaining = max(0, 10 - elapsed)
        st.markdown('<div class="timer-container">', unsafe_allow_html=True)
        st.progress(remaining / 10)
        st.markdown(f'<p style="text-align: center; color: white; font-size: 1em; font-weight: bold; margin-top: 5px;">⏱️ {int(remaining)}s</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Answer buttons - 2x2 grid for Kahoot style
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Determine grid layout based on number of options
        num_options = len(q['options'])
        if num_options <= 2:
            cols = st.columns(2)
        elif num_options == 3:
            cols = st.columns(3)
        else:
            # 2x2 grid for 4 options
            row1 = st.columns(2)
            row2 = st.columns(2)
            cols = list(row1) + list(row2)
        
        for i, option in enumerate(q['options']):
            # Extract letter from option (e.g., "a) Answer" -> "a")
            choice = option.split(')')[0].strip().lower()
            
            with cols[i]:
                # Add geometric shapes like Kahoot
                shapes = ["🔺", "💠", "⭕", "🟩"]
                shape = shapes[i] if i < len(shapes) else ""
                if st.button(f"{shape}\n\n{option}", key=f"opt_{choice}", use_container_width=True):
                    st.session_state.client.send_answer(choice)
                    st.session_state.answer_sent = True
                    st.rerun()
        
    elif st.session_state.answer_sent and st.session_state.current_question:
        st.markdown('<div class="status-waiting">✓ Answer submitted! Waiting for results...</div>', unsafe_allow_html=True)
        
    elif st.session_state.connected and not st.session_state.quiz_started:
        st.markdown('<div class="status-waiting">⏳ Waiting for quiz to start...<br>The host will begin the game soon!</div>', unsafe_allow_html=True)
    
    # Show scores
    if st.session_state.scores and not st.session_state.ranking:
        st.markdown('<div class="score-board">', unsafe_allow_html=True)
        st.markdown('<div class="score-title">📊 Leaderboard</div>', unsafe_allow_html=True)
        
        # Sort scores
        sorted_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (user, score) in enumerate(sorted_scores, 1):
            is_current = user == st.session_state.client.username
            class_name = "score-entry current-user" if is_current else "score-entry"
            medal = ""
            if rank == 1:
                medal = "🥇 "
            elif rank == 2:
                medal = "🥈 "
            elif rank == 3:
                medal = "🥉 "
            
            st.markdown(f'<div class="{class_name}">{medal}{rank}. {user} - {score} pts</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show final ranking
    if st.session_state.ranking:
        st.markdown('<div class="ranking-container">', unsafe_allow_html=True)
        st.markdown('<div class="ranking-title">🏆 FINAL RESULTS 🏆</div>', unsafe_allow_html=True)
        
        entries = st.session_state.ranking.split(" | ")
        
        for i, entry in enumerate(entries):
            rank_class = f"rank-{i+1}" if i < 3 else "rank-entry"
            medals = ["🥇", "🥈", "🥉"]
            medal = medals[i] if i < 3 else "🏅"
            st.markdown(f'<div class="rank-entry {rank_class}">{medal} {entry}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.balloons()
    
    # Activity feed in sidebar (non-intrusive)
    with st.sidebar:
        st.markdown("### 📢 Activity Feed")
        st.markdown(f"**Connected as:** {st.session_state.client.username}")
        st.markdown("---")
        
        # Show last 15 messages
        if st.session_state.messages:
            for msg_type, content in st.session_state.messages[-15:]:
                if "correctly" in content.lower() and st.session_state.client.username in content:
                    st.success(f"✓ {content}")
                elif "incorrectly" in content.lower() and st.session_state.client.username in content:
                    st.error(f"✗ {content}")
                elif "joined" in content.lower():
                    st.info(f"👋 {content}")
                elif "starting" in content.lower():
                    st.success(f"🚀 {content}")
                elif "finished" in content.lower():
                    st.success(f"🏁 {content}")
                elif "time's up" in content.lower():
                    st.warning("⏰ Time's up!")
                else:
                    st.caption(f"📢 {content}")
        else:
            st.caption("No activity yet...")
        
        st.markdown("---")
        if st.button("🚪 Disconnect", use_container_width=True):
            if st.session_state.client:
                st.session_state.client.disconnect()
            st.session_state.clear()
            st.rerun()
    
    # Auto-refresh to keep checking for messages
    if st.session_state.connected and not st.session_state.ranking:
        time.sleep(0.3)
        st.rerun()
