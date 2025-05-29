import streamlit as st
import openai
import os
from dotenv import load_dotenv
import requests
from PIL import Image
import io
import time
import random

# Load API keys
load_dotenv()
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# Set page config
st.set_page_config("Nani's Recipe AI", "👵", layout="wide")

# Session state setup
for key in ["messages", "recipe_count", "is_loading", "awaiting_clarification"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "messages" else False

LOADING_MESSAGES = [
    "Nani soch rahi hai... 🤔",
    "Masale check kar rahi hun... 🌶️",
    "Kitchen mein dekh rahi hun... 🥘"
]

# Function: Ask max 2 clarifying questions
@st.cache_data(show_spinner=False)
def get_recipe_from_nani(ingredients, user_preferences=""):
    prompt = f"""
    You are Nani, a loving Indian grandmother.
    Ask max 2 clarifying questions (spice level, time, diet) in warm Hinglish.
    Ingredients: {ingredients}
    Preferences: {user_preferences}

    Response in warm Hinglish only. Format:
    Arre beta! Perfect ingredients hai! ❤️\n\n[Ask 2 short, caring questions]\n\nBatao mujhe, phir main perfect recipe banakar dungi!
    """
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Function: Final recipe generation
@st.cache_data(show_spinner=False)
def get_final_recipe_from_nani(ingredients, preferences):
    prompt = f"""
    You are Nani, an Indian grandma. Make a recipe in 1–3 steps, Hinglish, max 25 min.
    Ingredients: {ingredients}
    Preferences: {preferences}

    Format:
    **🍳 Recipe: [Name]**
    **Time:** X mins | **Serves:** X

    **Step 1:** ....
    **Step 2:** ....

    **Nani's Tip:** .... ❤️

    End with: "Shabash beta!"
    """
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=500,
        temperature=0.8
    )
    return response.choices[0].text.strip()

# Function: Generate image
@st.cache_data(show_spinner=False)
def generate_dish_image(recipe_name):
    prompt = f"A homemade {recipe_name}, Indian kitchen setup, natural light"
    img_url = openai.Image.create(prompt=prompt, n=1, size="512x512")['data'][0]['url']
    img = Image.open(io.BytesIO(requests.get(img_url).content))
    return img

# Chat UI
st.title("👵 Nani's Recipe AI")
chat_box = st.container()

# Handle new message
with st.form("chat", clear_on_submit=True):
    user_input = st.text_input("What ingredients do you have, beta?", key="input")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.is_loading = True
    st.rerun()

# Render chat
with chat_box:
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Nani:** {msg['content']}")
            if 'image' in msg:
                st.image(msg['image'])

# Loading + respond
if st.session_state.is_loading:
    # Show loader
    st.markdown(f"**Nani:** {random.choice(LOADING_MESSAGES)}")
    time.sleep(2)
    
    user_msg = [m for m in st.session_state.messages if m['role'] == 'user'][-1]['content']

    if not st.session_state.awaiting_clarification:
        response = get_recipe_from_nani(user_msg)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.awaiting_clarification = True
    else:
        ingredients = next(m['content'] for m in st.session_state.messages if m['role'] == 'user')
        preferences = user_msg
        recipe = get_final_recipe_from_nani(ingredients, preferences)
        name_line = next((line for line in recipe.split('\n') if '**🍳 Recipe:' in line), "")
        recipe_name = name_line.replace("**🍳 Recipe:", "").replace("**", "").strip()
        image = generate_dish_image(recipe_name)
        st.session_state.messages.append({"role": "assistant", "content": recipe, "image": image})
        st.session_state.awaiting_clarification = False

    st.session_state.recipe_count = st.session_state.recipe_count + 1
    st.session_state.is_loading = False
    st.rerun()
