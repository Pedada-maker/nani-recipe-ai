import streamlit as st
import openai
import os
from dotenv import load_dotenv
import requests
from PIL import Image
import io
import time
import random

# Load environment variables for local development
load_dotenv()

# Set up OpenAI API key (prioritize Streamlit secrets, fallback to local .env)
try:
    openai_key = st.secrets['OPENAI_API_KEY']
except:
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        st.error("⚠️ OpenAI API Key not found! Please add it to Streamlit secrets.")
        st.stop()

# Set OpenAI API key (0.28 style)
openai.api_key = openai_key

# Page configuration
st.set_page_config(
    page_title="Nani's Recipe AI",
    page_icon="👵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with mobile-first responsive design
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500;700&display=swap');
    
    /* Main background */
    .stApp {
        background-color: #f1f5f9;
        font-family: 'Work Sans', sans-serif;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header styling */
    .main-header {
        background-color: #f1f5f9;
        padding: 1rem;
        text-align: center;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .main-title {
        color: #0e161b;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    
    .tagline {
        color: #4e7a97;
        font-size: 0.9rem;
        margin-top: 0.25rem;
        font-style: italic;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 100%;
        margin: 0 auto;
        padding: 1rem;
        min-height: 60vh;
        max-height: 60vh;
        overflow-y: auto;
    }
    
    /* Message styling */
    .message-container {
        display: flex;
        margin: 1rem 0;
        gap: 0.75rem;
        align-items: flex-end;
    }
    
    .message-container.user {
        justify-content: flex-end;
    }
    
    .avatar {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        background-size: cover;
        background-position: center;
        flex-shrink: 0;
    }
    
    .nani-avatar {
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23fbbf24"/><text x="50" y="60" text-anchor="middle" font-size="40">👵</text></svg>');
    }
    
    .user-avatar {
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%231993e5"/><text x="50" y="60" text-anchor="middle" font-size="40">👤</text></svg>');
    }
    
    .message-content {
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    .user-message {
        background-color: #1993e5;
        color: white;
        border-bottom-right-radius: 0.25rem;
    }
    
    .nani-message {
        background-color: #e7eef3;
        color: #0e161b;
        border-bottom-left-radius: 0.25rem;
    }
    
    .message-label {
        font-size: 0.75rem;
        color: #4e7a97;
        margin-bottom: 0.25rem;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        background-color: #e7eef3;
        border-radius: 1rem;
        border-bottom-left-radius: 0.25rem;
        max-width: 70%;
    }
    
    .loading-dots {
        display: flex;
        gap: 0.25rem;
    }
    
    .loading-dot {
        width: 0.5rem;
        height: 0.5rem;
        background-color: #4e7a97;
        border-radius: 50%;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    .loading-dot:nth-child(2) { animation-delay: 0.2s; }
    .loading-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes pulse {
        0%, 80%, 100% { opacity: 0.3; }
        40% { opacity: 1; }
    }
    
    /* Recipe card styling */
    .recipe-card {
        background-color: white;
        border-radius: 1rem;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .recipe-image {
        width: 100%;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .recipe-title {
        color: #0e161b;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .recipe-meta {
        color: #4e7a97;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .recipe-steps {
        border-top: 1px solid #e2e8f0;
        padding-top: 1rem;
    }
    
    .recipe-step {
        display: flex;
        gap: 1rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .step-number {
        color: #4e7a97;
        font-weight: 500;
        min-width: 4rem;
        font-size: 0.85rem;
    }
    
    .step-content {
        color: #0e161b;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Input section */
    .input-section {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #f1f5f9;
        padding: 1rem;
        border-top: 1px solid #e2e8f0;
    }
    
    .input-container {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        background-color: #e7eef3;
        border-radius: 1.5rem;
        padding: 0.5rem;
    }
    
    .voice-input-btn {
        background-color: #fbbf24;
        border: none;
        border-radius: 50%;
        width: 3rem;
        height: 3rem;
        font-size: 1.25rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    
    .voice-input-btn:hover {
        background-color: #f59e0b;
        transform: scale(1.05);
    }
    
    .voice-input-btn.recording {
        background-color: #ef4444;
        animation: pulse-red 1s ease-in-out infinite;
    }
    
    @keyframes pulse-red {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .text-input {
        flex: 1;
        border: none;
        background: transparent;
        padding: 0.75rem;
        font-size: 1rem;
        outline: none;
        color: #0e161b;
    }
    
    .text-input::placeholder {
        color: #4e7a97;
    }
    
    .send-btn {
        background-color: #1993e5;
        color: white;
        border: none;
        border-radius: 1.25rem;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .send-btn:hover {
        background-color: #1e40af;
    }
    
    .send-btn:disabled {
        background-color: #94a3b8;
        cursor: not-allowed;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .chat-container {
            padding: 0.75rem;
            margin-bottom: 5rem;
        }
        
        .message-content {
            max-width: 85%;
            font-size: 0.9rem;
        }
        
        .main-title {
            font-size: 1.25rem;
        }
        
        .tagline {
            font-size: 0.8rem;
        }
        
        .voice-input-btn {
            width: 2.5rem;
            height: 2.5rem;
            font-size: 1rem;
        }
        
        .recipe-card {
            margin: 0.75rem 0;
            padding: 0.75rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'recipe_count' not in st.session_state:
    st.session_state.recipe_count = 0
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False
if 'awaiting_clarification' not in st.session_state:
    st.session_state.awaiting_clarification = False

# Nani's loading messages
LOADING_MESSAGES = [
    "Nani soch rahi hai... 🤔",
    "Recipe bana rahi hun, beta... 👵",
    "Masale check kar rahi hun... 🌶️",
    "Kitchen mein dekh rahi hun... 🥘",
    "Gharelu nuskha yaad kar rahi hun... 💭",
    "Pyaar se recipe banati hun... ❤️"
]

# Voice recognition JavaScript
voice_js = """
<script>
let recognition;
let isRecording = false;

function startVoiceInput() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Voice input not supported in this browser, beta!');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.lang = 'hi-IN';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = function() {
        isRecording = true;
        document.getElementById('voice-btn').classList.add('recording');
        document.getElementById('voice-btn').innerHTML = '🎙️';
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('text-input').value = transcript;
        document.getElementById('text-input').focus();
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        alert('Kuch problem ho gayi, beta. Phir se try karo!');
    };
    
    recognition.onend = function() {
        isRecording = false;
        document.getElementById('voice-btn').classList.remove('recording');
        document.getElementById('voice-btn').innerHTML = '🎤';
    };
    
    recognition.start();
}

function toggleVoiceInput() {
    if (isRecording) {
        recognition.stop();
    } else {
        startVoiceInput();
    }
}
</script>
"""

def get_recipe_from_nani(ingredients, user_preferences=""):
    """Generate recipe using OpenAI GPT-4 with Nani's persona"""
    try:
        prompt = f"""
        You are Nani, a loving Indian grandmother who speaks in warm Hinglish (60% English, 40% Hindi). You're helping your grandchild cook with available ingredients.

        PERSONA:
        - Warm, caring, uses "beta", "arre", "shabash"
        - Mix Hindi words naturally: "dal", "chawal", "masala", "tadka", "ghee"
        - Always encouraging and loving
        - Mentions home remedies and cooking tips
        - Uses traditional cooking wisdom

        USER'S INGREDIENTS: {ingredients}
        USER PREFERENCES: {user_preferences}

        FIRST, ask 1-2 clarifying questions about:
        - How spicy they want it (teekha?)
        - Any dietary restrictions
        - Available cooking time
        - Basic spices available (haldi, jeera, etc.)

        IMPORTANT: Only ask questions first. Don't give recipe yet. Be warm and caring in your questions.

        FORMAT:
        Arre beta! Perfect ingredients hai aapke paas! ❤️

        [Ask 2 warm, caring questions in Hinglish]

        Batao mujhe, phir main perfect recipe banakar dungi!
        """
        
        # Using OpenAI 0.28 style
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=300,
            temperature=0.8
        )
        
        return response.choices[0].text.strip()
        
    except Exception as e:
        return f"Arre beta, kuch gadbad ho gayi! 😅 Phir se try karo. Error: {str(e)}"

def get_final_recipe_from_nani(ingredients, preferences):
    """Generate final recipe after clarifications"""
    try:
        prompt = f"""
        You are Nani, a loving Indian grandmother. Create a recipe using these ingredients: {ingredients}
        User preferences: {preferences}

        STRICT REQUIREMENTS:
        1. Speak in warm Hinglish (60% English, 40% Hindi)
        2. Maximum 3 steps, but optimize for time (prefer 1-2 steps if possible)
        3. Total cooking time: 15-25 minutes maximum
        4. Traditional Indian home cooking style
        5. Include basic spices (assume haldi, namak, jeera available)
        6. Be encouraging and loving

        FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
        **🍳 Recipe: [Hinglish Recipe Name]**

        **Time:** [X] minutes | **Serves:** [X] 

        **Step 1 ([X] min):** [Clear instruction in Hinglish]

        **Step 2 ([X] min):** [If needed - Clear instruction in Hinglish]

        **Step 3 ([X] min):** [If needed - Clear instruction in Hinglish]

        **Nani's Tip:** [One loving tip with Hindi words] ❤️

        End with encouraging words like "Shabash beta!" or "Bahut accha bana hoga!"
        """
        
        # Using OpenAI 0.28 style
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=500,
            temperature=0.8
        )
        
        return response.choices[0].text.strip()
        
    except Exception as e:
        return f"Arre beta, kuch problem hai! 😅 Phir se try karo: {str(e)}"

def generate_dish_image(recipe_name):
    """Generate home-style Indian dish image"""
    try:
        prompt = f"A homemade {recipe_name}, traditional Indian home cooking style, served in simple Indian kitchen utensils, warm home lighting, authentic Indian household setting, realistic, cozy atmosphere"
        
        # Using OpenAI 0.28 style for DALL-E
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        image_url = response['data'][0]['url']
        img_response = requests.get(image_url)
        img = Image.open(io.BytesIO(img_response.content))
        
        return img
        
    except Exception as e:
        st.error(f"Image nahi bana payi, beta: {str(e)}")
        return None

# Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">👵 Nani's Recipe AI</h1>
    <p class="tagline">Nani ke gharelu nuskhe—no more crying over onions or complicated recipes!</p>
</div>
""", unsafe_allow_html=True)

# Chat container
chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Welcome message if no messages
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="message-container">
            <div class="avatar nani-avatar"></div>
            <div>
                <div class="message-label">Nani</div>
                <div class="message-content nani-message">
                    Namaste beta! Main tumhari Nani hun. Batao kya hai aaj fridge mein? Main tumhare liye perfect recipe banakar dungi! ❤️
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="message-container user">
                <div>
                    <div class="message-label" style="text-align: right;">You</div>
                    <div class="message-content user-message">{message["content"]}</div>
                </div>
                <div class="avatar user-avatar"></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-container">
                <div class="avatar nani-avatar"></div>
                <div>
                    <div class="message-label">Nani</div>
                    <div class="message-content nani-message">{message["content"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show recipe card if there's an image
            if "image" in message:
                with st.container():
                    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                    st.image(message["image"], use_column_width=True, caption="Dekho beta, aisa dikhega tumhara pyaara khana! 🍽️")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show loading animation
    if st.session_state.is_loading:
        loading_msg = random.choice(LOADING_MESSAGES)
        st.markdown(f"""
        <div class="message-container">
            <div class="avatar nani-avatar"></div>
            <div>
                <div class="message-label">Nani</div>
                <div class="loading-container">
                    <span>{loading_msg}</span>
                    <div class="loading-dots">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Input section
st.markdown("""
<div class="input-section">
    <div class="input-container">
        <button class="voice-input-btn" id="voice-btn" onclick="toggleVoiceInput()" title="Voice input - Nani sunegi!">🎤</button>
        <input type="text" class="text-input" id="text-input" placeholder="Kya hai aaj fridge mein, beta?" />
        <button class="send-btn" onclick="document.getElementById('send-form').submit()">Chalo, Nani ke saath pakao! 🍳</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Hidden form for submission
with st.form("send-form", clear_on_submit=True):
    user_input = st.text_input("user_input", label_visibility="collapsed", key="hidden_input")
    submitted = st.form_submit_button("Send", label_visibility="collapsed")

# Process input
if submitted and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Set loading state
    st.session_state.is_loading = True
    st.rerun()

# Handle loading state
if st.session_state.is_loading:
    time.sleep(2)  # Show loading for 2 seconds
    st.session_state.is_loading = False
    
    # Get the last user message
    last_user_message = st.session_state.messages[-1]["content"]
    
    # Check if we're awaiting clarification or giving recipe
    if not st.session_state.awaiting_clarification:
        # First interaction - ask clarifying questions
        response = get_recipe_from_nani(last_user_message)
        st.session_state.awaiting_clarification = True
    else:
        # User has answered questions - give final recipe
        # Get ingredients from earlier messages
        ingredients = ""
        preferences = last_user_message
        
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                ingredients = msg["content"]
                break
        
        response = get_final_recipe_from_nani(ingredients, preferences)
        
        # Generate image for final recipe
        recipe_lines = response.split('\n')
        recipe_name = "Indian dish"
        for line in recipe_lines:
            if '**🍳 Recipe:' in line:
                recipe_name = line.replace('**🍳 Recipe:', '').replace('**', '').strip()
                break
        
        dish_image = generate_dish_image(recipe_name)
        
        # Add image to response
        bot_message = {"role": "assistant", "content": response}
        if dish_image:
            bot_message["image"] = dish_image
        
        st.session_state.messages.append(bot_message)
        st.session_state.recipe_count += 1
        st.session_state.awaiting_clarification = False
        st.rerun()
    
    # Add response without image for clarification
    if st.session_state.awaiting_clarification:
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# Add voice recognition JavaScript
st.markdown(voice_js, unsafe_allow_html=True)

# Sidebar stats
if st.session_state.recipe_count > 0:
    with st.sidebar:
        st.success(f"🎉 Nani ke recipes aaj: {st.session_state.recipe_count}")
        if st.button("Chat clear karo"):
            st.session_state.messages = []
            st.session_state.recipe_count = 0
            st.session_state.awaiting_clarification = False
            st.rerun()

# JavaScript to sync text input
sync_js = """
<script>
// Sync hidden input with visible input
document.addEventListener('DOMContentLoaded', function() {
    const visibleInput = document.getElementById('text-input');
    const hiddenInput = document.querySelector('input[aria-label="user_input"]');
    
    if (visibleInput && hiddenInput) {
        visibleInput.addEventListener('input', function() {
            hiddenInput.value = this.value;
        });
        
        visibleInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                document.getElementById('send-form').querySelector('button').click();
            }
        });
    }
});
</script>
"""

st.markdown(sync_js, unsafe_allow_html=True)