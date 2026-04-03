import streamlit as st
import google.generativeai as genai

# 1. Page Configuration (Added "wide" layout for a better look on desktop)
st.set_page_config(page_title="My Custom AI", page_icon="✨", layout="centered")

# --- UI UPGRADE: The Sidebar ---
with st.sidebar:
    st.header("⚙️ Chat Settings")
    
    # Let the user choose the AI's "brain" dynamically!
    selected_model = st.selectbox(
        "Choose an AI Model",
        ["gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-3-flash-preview"]
    )
    
    st.divider() # Adds a clean horizontal line
    
    # UI UPGRADE: Clear Chat Button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun() # Refreshes the app instantly

# Main Page Header
st.title("Welcome to uh some random ai! ✨")
st.caption("A custom AI assistant built with love <3")

# Load API Key safely
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Connect to the model chosen in the sidebar
model = genai.GenerativeModel(selected_model)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI UPGRADE: Custom Avatars ---
# We assign specific emojis to the user and the assistant
avatars = {"user": "🧑‍💻", "assistant": "🤖"}

# Display previous messages with the new avatars
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatars[message["role"]]):
        st.markdown(message["content"])

# Chat Input & AI Response
if user_prompt := st.chat_input("Ask me anything..."):
    
    # Show user message with avatar
    st.chat_message("user", avatar=avatars["user"]).markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Get response
    response = model.generate_content(user_prompt)

    # Show AI response with avatar
    with st.chat_message("assistant", avatar=avatars["assistant"]):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
