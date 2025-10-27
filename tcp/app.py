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
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #00BFFF;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .question-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00BFFF;
        margin: 10px 0;
    }
    .score-box {
        background-color: #f0fff0;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #32CD32;
    }
    .correct {
        color: #32CD32;
        font-weight: bold;
    }
    .incorrect {
        color: #FF6347;
        font-weight: bold;
    }
    .broadcast {
        color: #FFD700;
        font-style: italic;
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
st.markdown('<div class="main-header">🎯 QUIZNET TCP QUIZ 🎯</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Real-time Multiplayer Quiz!</p>', unsafe_allow_html=True)

# Connection section
if not st.session_state.connected:
    st.markdown("---")
    st.subheader("📡 Connect to Quiz Server")
    
    col1, col2 = st.columns(2)
    with col1:
        server_ip = st.text_input("Server IP", value="127.0.0.1")
    with col2:
        username = st.text_input("Username", value="")
    
    if st.button("🚀 Join Quiz", type="primary"):
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
else:
    # Connected - show quiz interface
    st.success(f"✅ Connected as **{st.session_state.client.username}**")
    
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
        
        st.markdown("---")
        st.markdown(f'<div class="question-box">', unsafe_allow_html=True)
        st.markdown(f"### 📝 Question {q['id']}")
        st.markdown(f"**{q['text']}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display options as buttons
        st.write("**Choose your answer:**")
        cols = st.columns(3)
        
        for i, option in enumerate(q['options']):
            # Extract letter from option (e.g., "a) Answer" -> "a")
            choice = option.split(')')[0].strip().lower()
            
            with cols[i]:
                if st.button(option, key=f"opt_{choice}", use_container_width=True):
                    st.session_state.client.send_answer(choice)
                    st.session_state.answer_sent = True
                    st.rerun()
        
        # Show timer
        elapsed = time.time() - q['start_time']
        remaining = max(0, 10 - int(elapsed))
        st.progress(remaining / 10)
        st.caption(f"⏱️ Time remaining: {remaining} seconds")
        
    elif st.session_state.answer_sent and st.session_state.current_question:
        st.info("✓ Answer submitted! Waiting for results...")
    elif st.session_state.connected and not st.session_state.quiz_started:
        st.info("⏳ Waiting for quiz to start... The server admin will start the quiz when ready.")
    
    # Show scores
    if st.session_state.scores:
        st.markdown("---")
        st.markdown('<div class="score-box">', unsafe_allow_html=True)
        st.subheader("📊 Current Scores")
        
        # Sort scores
        sorted_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
        
        for user, score in sorted_scores:
            if user == st.session_state.client.username:
                st.markdown(f"**👉 {user}: {score} points**")
            else:
                st.markdown(f"{user}: {score} points")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show final ranking
    if st.session_state.ranking:
        st.markdown("---")
        st.balloons()
        st.subheader("🏆 FINAL RANKINGS 🏆")
        
        entries = st.session_state.ranking.split(" | ")
        medals = ["🥇", "🥈", "🥉"]
        
        for i, entry in enumerate(entries):
            medal = medals[i] if i < 3 else "  "
            st.markdown(f"{medal} **{entry}**")
    
    # Show messages
    if st.session_state.messages:
        st.markdown("---")
        st.subheader("📢 Activity Feed")
        
        # Show last 10 messages
        for msg_type, content in st.session_state.messages[-10:]:
            if "correctly" in content.lower() and st.session_state.client.username in content:
                st.markdown(f'<p class="correct">✓ {content}</p>', unsafe_allow_html=True)
            elif "incorrectly" in content.lower() and st.session_state.client.username in content:
                st.markdown(f'<p class="incorrect">✗ {content}</p>', unsafe_allow_html=True)
            elif "joined" in content.lower():
                st.info(f"👋 {content}")
            elif "starting" in content.lower():
                st.success(f"🚀 {content}")
            elif "finished" in content.lower():
                st.success(f"🏁 {content}")
            elif "time's up" in content.lower():
                st.warning(content)
            else:
                st.markdown(f'<p class="broadcast">📢 {content}</p>', unsafe_allow_html=True)
    
    # Auto-refresh to keep checking for messages
    if st.session_state.connected and not st.session_state.ranking:
        time.sleep(0.3)
        st.rerun()
    
    # Disconnect button
    st.markdown("---")
    if st.button("🚪 Disconnect"):
        if st.session_state.client:
            st.session_state.client.disconnect()
        st.session_state.clear()
        st.rerun()
