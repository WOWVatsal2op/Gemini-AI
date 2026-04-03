import streamlit as st
import google.generativeai as genai
from streamlit_local_storage import LocalStorage
import datetime

# Initialize Local Storage
localS = LocalStorage()

st.set_page_config(page_title="Our Private AI", page_icon="💖", layout="centered")

# --- 1. LOAD MASTER FOLDER FROM BROWSER ---
# We look for "all_chats" which is a dictionary holding all conversations
all_chats = localS.getItem("all_chats")

# If it's a new user or empty, create the first default chat
if not all_chats or not isinstance(all_chats, dict):
    all_chats = {"Chat 1": []}
    localS.setItem("all_chats", all_chats)

# Set the active chat in session state
if "current_chat_id" not in st.session_state:
    # Default to the first available chat
    st.session_state.current_chat_id = list(all_chats.keys())[0]

# Failsafe: if the current chat id somehow got deleted, reset it
if st.session_state.current_chat_id not in all_chats:
    all_chats[st.session_state.current_chat_id] = []

# Sync the active messages so the screen displays the right chat
st.session_state.messages = all_chats[st.session_state.current_chat_id]

# --- 2. SIDEBAR & SETTINGS ---
with st.sidebar:
    st.title("⚙️ Controls")
    
    # NEW CHAT BUTTON
    if st.button("➕ New Chat", use_container_width=True):
        # Generate a unique name using the current time so they don't overwrite
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        new_chat_name = f"Chat at {time_str}"
        
        # Create a blank list for this new chat and switch to it
        all_chats[new_chat_name] = []
        st.session_state.current_chat_id = new_chat_name
        localS.setItem("all_chats", all_chats)
        st.rerun()

    st.divider()

    # AI MODEL SELECTION
    selected_model = st.selectbox(
        "🧠 Choose AI Model",
        ["gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-3-flash-preview"]
    )

    st.divider()

    # RECENT CHATS LIST
    st.subheader("📝 Recent Chats")
    chat_names = list(all_chats.keys())
    
    # Radio buttons let the user click between different histories
    selected_chat = st.radio(
        "Switch conversation:", 
        chat_names, 
        index=chat_names.index(st.session_state.current_chat_id)
    )
    
    # If they click a different radio button, switch the active chat
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.rerun()

    st.divider()

    # DELETE CHAT BUTTON
    if st.button("🗑️ Delete This Chat", use_container_width=True):
        del all_chats[st.session_state.current_chat_id]
        
        # Prevent the app from crashing if they delete all chats
        if len(all_chats) == 0:
            all_chats = {"Chat 1": []} 
            
        st.session_state.current_chat_id = list(all_chats.keys())[0]
        localS.setItem("all_chats", all_chats)
        st.rerun()

# --- 3. AI SETUP ---
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel(selected_model)

# --- 4. MAIN PAGE UI ---
st.title(f"{st.session_state.current_chat_id} ✨")
avatars = {"user": "🧑‍💻", "assistant": "🤖"}

# Display the messages for the currently selected chat
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatars[message["role"]]):
        st.markdown(message["content"])

# --- 5. CHAT LOGIC ---
if user_prompt := st.chat_input("Message your AI..."):
    
    # Display & Save User Message
    st.chat_message("user", avatar=avatars["user"]).markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # Get AI Response
    response = model.generate_content(user_prompt)
    
    # Display & Save AI Response
    with st.chat_message("assistant", avatar=avatars["assistant"]):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})

    # Save the updated list back into the master folder in the browser!
    all_chats[st.session_state.current_chat_id] = st.session_state.messages
    localS.setItem("all_chats", all_chats)
