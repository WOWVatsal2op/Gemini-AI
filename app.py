import streamlit as st
import google.generativeai as genai
from streamlit_local_storage import LocalStorage

# Initialize Local Storage
localS = LocalStorage()

st.set_page_config(page_title="Our Private AI", page_icon="💖")

# --- 1. LOAD HISTORY FROM BROWSER ---
# This checks the user's computer for a file named "stored_chat"
if "messages" not in st.session_state:
    saved_chats = localS.getItem("stored_chat")
    if saved_chats:
        st.session_state.messages = saved_chats
    else:
        st.session_state.messages = []

# --- 2. SIDEBAR & SETTINGS ---
with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Clear My History"):
        st.session_state.messages = []
        localS.deleteItem("stored_chat") # Wipes it from the browser too
        st.rerun()

# --- 3. AI SETUP ---
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. CHAT LOGIC ---
if user_prompt := st.chat_input("Message your AI..."):
    # Display & Save User Message
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # Get AI Response
    response = model.generate_content(user_prompt)
    
    # Display & Save AI Response
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})

    # --- 5. SAVE TO BROWSER ---
    # This sends the updated list back to the user's local storage
    localS.setItem("stored_chat", st.session_state.messages)
