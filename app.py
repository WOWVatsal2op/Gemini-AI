import streamlit as st
import google.generativeai as genai
from streamlit_local_storage import LocalStorage
import datetime

# Initialize Local Storage
localS = LocalStorage()

st.set_page_config(page_title="My Private AI", page_icon="💖", layout="centered")

# --- CUSTOM CSS: THE EXACT LAYOUT & MODERN THEME FROM YOUR DESIGN (image_3.png) ---
custom_css = """
<style>
    /* Main App Background (Deeper Gray/Black) */
    .stApp {
        background-color: #212121;
        color: #ECECEC;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 1. Sidebar Panel (Slightly Lighter Vibe than design, but defined panel) */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A !important;
        border-right: none !important;
        box-shadow: 5px 0px 15px rgba(0, 0, 0, 0.4);
        padding-top: 1rem;
    }

    /* 2. Side-by-Side Control Buttons in Sidebar (Floating Card) */
    .stButton>button {
        border-radius: 25px !important;
        background-color: #2F2F2F !important;
        color: #ECECEC !important;
        border: 1px solid #444 !important;
        transition: all 0.3s ease;
        use-container-width: true; /* Ensure full sidebar width utilization */
    }
    .stButton>button:hover {
        background-color: #3F3F3F !important;
        border-color: #666 !important;
        transform: translateY(-2px);
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }

    /* 3. The Custom Chat Selection List (Pill-shaped, Sharp Red Highlighting) */
    /* Make the radio button list look like pill buttons */
    div.stRadio > div[role="radiogroup"] > label {
        display: block;
        padding: 0.75rem 1.5rem;
        margin-bottom: 0.5rem;
        border-radius: 25px;
        background-color: #2F2F2F;
        border: 1px solid #444;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    div.stRadio > div[role="radiogroup"] > label:hover {
        background-color: #3F3F3F;
        border-color: #666;
    }

    /* Target the ACTIVE/SELECTED chat name for special highlight style */
    div.stRadio > div[role="radiogroup"] > label[aria-selected="true"] {
        background-color: #3F3F3F !important;
        border-color: #999 !important;
        color: #ECECEC !important;
        box-shadow: 0px 4px 10px rgba(255, 255, 255, 0.1);
    }
    
    /* Hide the default tiny selection circle, replaced with active button style above */
    div.stRadio > div[role="radiogroup"] > label > div[data-testid="stRadioControlContainer"] {
        display: none !important;
    }

    /* 4. Chat Bubbles (Rounded Rectangle, Left/Right Align) */
    /* Default (Left-aligned Bot/Assistant) bubble styling - Darker */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1A1A1A;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #333;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.4);
    }
    
    /* Custom User Bubble (Right-aligned, Lighter Contrast) styling */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #2F2F2F;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #444;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }

    /* 5. The Pill-Shaped Text Input (Minimal, Floating Vibe) */
    [data-testid="stChatInput"] {
        background-color: #2F2F2F !important;
        border-radius: 25px !important;
        border: 1px solid #444 !important;
        box-shadow: 0px -5px 15px rgba(0, 0, 0, 0.1) !important;
        margin-top: 1rem;
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

# --- 2. SIDEBAR & SETTINGS (Following your design layout) ---
with st.sidebar:
    st.title("⚙️ Controls")
    
    # Combined Controls Section (Side-by-side buttons)
    cols = st.columns(2)
    with cols[0]:
        if st.button("➕ New Chat"):
            time_str = datetime.datetime.now().strftime("%I:%M %p")
            new_chat_name = f"Chat at {time_str}"
            all_chats[new_chat_name] = []
            st.session_state.current_chat_id = new_chat_name
            localS.setItem("all_chats", all_chats)
            st.rerun()
    with cols[1]:
        if st.button("🗑️ Delete Chat"):
            del all_chats[st.session_state.current_chat_id]
            if len(all_chats) == 0:
                all_chats = {"Chat 1": []} 
            st.session_state.current_chat_id = list(all_chats.keys())[0]
            localS.setItem("all_chats", all_chats)
            st.rerun()

    st.divider()

    selected_model = st.selectbox(
        "🧠 Choose AI Model",
        ["gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-3-flash-preview"]
    )

    st.divider()

    # The Custom Chat Selection List (Styled with radio buttons)
    st.subheader("📝 Recent Chats")
    chat_names = list(all_chats.keys())
    
    selected_chat = st.radio(
        "Switch conversation:", 
        chat_names, 
        index=chat_names.index(st.session_state.current_chat_id),
        label_visibility="collapsed" # Hides the label to save space
    )
    
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.rerun()

# --- 3. AI SETUP ---
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel(selected_model)

# --- 4. MAIN PAGE UI (The Conversation Area) ---
st.title(f"{st.session_state.current_chat_id} ✨")
avatars = {"user": "🧑‍💻", "assistant": "🤖"}

# Display messages, alternating roles/colors via CSS
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatars[message["role"]]):
        st.markdown(message["content"])

# --- 5. CHAT LOGIC ---
if user_prompt := st.chat_input("Write your message here..."):
    
    # Display & Save User Message (Will be the lighter, right-aligned bubble)
    st.chat_message("user", avatar=avatars["user"]).markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # GET & INTERCEPT SECRET CODE FEATURE
    # If the user says exactly "143", the AI must reply with "I love you!"
    # instead of telling what it means.
    if user_prompt.strip() == "143":
        custom_response = "I love you! 💖"
        with st.chat_message("assistant", avatar=avatars["assistant"]):
            st.markdown(custom_response)
        st.session_state.messages.append({"role": "assistant", "content": custom_response})
        
    else:
        # Normal AI execution
        with st.chat_message("assistant", avatar=avatars["assistant"]):
            with st.spinner("🤖 Thinking..."):
                response = model.generate_content(user_prompt)
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    # Save the updated list back into the master folder in the browser
    all_chats[st.session_state.current_chat_id] = st.session_state.messages
    localS.setItem("all_chats", all_chats)
