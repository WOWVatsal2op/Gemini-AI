import streamlit as st
import google.generativeai as genai
from streamlit_local_storage import LocalStorage
import datetime

# Initialize Local Storage
localS = LocalStorage()

st.set_page_config(page_title="Our Private AI", page_icon="💖", layout="centered")

# --- UI UPGRADE: CUSTOM CSS FOR MODERN DARK THEME & FLOATING ELEMENTS ---
custom_css = """
<style>
    /* Main App Background (Deep Gray/Black) */
    .stApp {
        background-color: #212121;
        color: #ECECEC;
    }
    
    /* Floating Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: none !important;
        box-shadow: 5px 0px 15px rgba(0, 0, 0, 0.4);
    }
    
    /* Styling the Chat Bubbles to look like floating cards */
    [data-testid="stChatMessage"] {
        background-color: #2F2F2F;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* Styling the Chat Input Box */
    [data-testid="stChatInput"] {
        background-color: #2F2F2F !important;
        border-radius: 25px !important;
        border: 1px solid #444 !important;
        box-shadow: 0px -5px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Floating modern buttons in the Sidebar */
    .stButton>button {
        border-radius: 12px !important;
        background-color: #2F2F2F !important;
        color: #ECECEC !important;
        border: 1px solid #444 !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3F3F3F !important;
        border-color: #666 !important;
        transform: translateY(-2px);
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 1. LOAD MASTER FOLDER FROM BROWSER ---
all_chats = localS.getItem("all_chats")

if not all_chats or not isinstance(all_chats, dict):
    all_chats = {"Chat 1": []}
    localS.setItem("all_chats", all_chats)

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = list(all_chats.keys())[0]

if st.session_state.current_chat_id not in all_chats:
    all_chats[st.session_state.current_chat_id] = []

st.session_state.messages = all_chats[st.session_state.current_chat_id]

# --- 2. SIDEBAR & SETTINGS ---
with st.sidebar:
    st.title("⚙️ Controls")
    
    if st.button("➕ New Chat", use_container_width=True):
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        new_chat_name = f"Chat at {time_str}"
        all_chats[new_chat_name] = []
        st.session_state.current_chat_id = new_chat_name
        localS.setItem("all_chats", all_chats)
        st.rerun()

    st.divider()

    selected_model = st.selectbox(
        "🧠 Choose AI Model",
        ["gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-3-flash-preview"]
    )

    st.divider()

    st.subheader("📝 Recent Chats")
    chat_names = list(all_chats.keys())
    
    selected_chat = st.radio(
        "Switch conversation:", 
        chat_names, 
        index=chat_names.index(st.session_state.current_chat_id)
    )
    
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.rerun()

    st.divider()

    if st.button("🗑️ Delete This Chat", use_container_width=True):
        del all_chats[st.session_state.current_chat_id]
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

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatars[message["role"]]):
        st.markdown(message["content"])

# --- 5. CHAT LOGIC ---
if user_prompt := st.chat_input("Message your AI..."):
    st.chat_message("user", avatar=avatars["user"]).markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    response = model.generate_content(user_prompt)
    
    with st.chat_message("assistant", avatar=avatars["assistant"]):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})

    all_chats[st.session_state.current_chat_id] = st.session_state.messages
    localS.setItem("all_chats", all_chats)
