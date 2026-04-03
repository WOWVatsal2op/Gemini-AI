import streamlit as st
import google.generativeai as genai
from streamlit_local_storage import LocalStorage
import datetime
import json

# Initialize Local Storage
localS = LocalStorage()

# --- APP CONFIG & PAGE TITLE ---
st.set_page_config(page_title="Our Private AI", page_icon="💖", layout="centered")

# --- CUSTOM CSS: MODERN DARK THEME, ABSTRACT BACKGROUND, & HIGHLIGHTED UI ---
custom_css = """
<style>
    /* 1. Root and Font Styling */
    :root {
        --color-background-main: #212121;
        --color-background-sidebar: #171717;
        --color-text-main: #ECECEC;
        --color-accent-highlight: #FFFFFF; /* High contrast for active state */
        --border-radius-main: 15px;
        --border-radius-pill: 25px;
        --shadow-main: 0px 4px 10px rgba(0, 0, 0, 0.4);
    }

    /* Main App Container */
    .stApp {
        background-color: var(--color-background-main);
        color: var(--color-text-main);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 2. Chat Bubble Styling (Alternating colors with rounded corners) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1A1A1A;
        border-radius: var(--border-radius-main);
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #333;
        box-shadow: var(--shadow-main);
    }
    
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #2F2F2F;
        border-radius: var(--border-radius-main);
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #444;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }

    /* 3. Floating Sidebar with Shadow */
    [data-testid="stSidebar"] {
        background-color: var(--color-background-sidebar) !important;
        border-right: none !important;
        box-shadow: 5px 0px 15px rgba(0, 0, 0, 0.4);
    }

    /* Sidebar Content Spacing */
    [data-testid="stSidebarContent"] {
        padding-top: 1rem;
    }

    /* 4. Custom Chat Selection List (Highlighted Box with Rounded Corners) */
    [data-testid="stSidebar"] div[data-testid="stBlock"] button {
        border-radius: var(--border-radius-main) !important;
        border: 1px solid transparent !important;
        background-color: transparent !important;
        color: var(--color-text-main) !important;
        transition: all 0.3s ease;
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        text-align: left;
    }

    /* Style for the *active/highlighted* chat name */
    [data-testid="stSidebar"] div[data-testid="stBlock"] button[disabled] {
        border-color: var(--color-accent-highlight) !important;
        background-color: #333 !important;
        color: var(--color-accent-highlight) !important;
        box-shadow: 0px 2px 5px rgba(255, 255, 255, 0.1);
    }

    [data-testid="stSidebar"] div[data-testid="stBlock"] button:hover:not([disabled]) {
        background-color: #2F2F2F !important;
        border-color: #444 !important;
        transform: translateY(-1px);
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }

    /* 5. Combined Buttons Section (Floating with shadow) */
    .controls-container {
        padding: 1rem;
        background-color: #2F2F2F;
        border-radius: var(--border-radius-main);
        box-shadow: var(--shadow-main);
        margin-bottom: 1.5rem;
        border: 1px solid #444;
    }
    .controls-container .stButton>button {
        border-radius: var(--border-radius-pill) !important;
    }

    /* 6. Abstract Background for Homepage ONLY */
    .homepage-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        background: linear-gradient(135deg, #0A0A0A 0%, #1A1A1A 50%, #291F30 100%);
        overflow: hidden;
    }
    
    .abstract-background {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.03) 0,
            rgba(255, 255, 255, 0.03) 2px,
            transparent 2px,
            transparent 20px
        );
        transform: rotate(15deg);
        opacity: 0.2;
    }
    
    /* Homepage content positioning */
    .homepage-content {
        margin-top: 5vh;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3rem;
    }
    .homepage-header {
        font-size: 3.5rem;
        font-weight: 800;
        color: var(--color-text-main);
        text-shadow: 0px 4px 10px rgba(255, 255, 255, 0.1);
    }
    .homepage-tagline {
        font-size: 1.2rem;
        color: #BBB;
    }
    
    /* Large floating buttons on the homepage */
    .homepage-buttons .stButton > button {
        border-radius: var(--border-radius-pill) !important;
        padding: 1.5rem 3rem !important;
        font-size: 1.1rem !important;
        min-width: 220px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- HELPER FUNCTIONS FOR APP FLOW ---
def go_to_homepage():
    st.session_state.current_page = "homepage"
    st.rerun()

def start_new_chat():
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    new_chat_name = f"Chat at {time_str}"
    
    # Reload chats from storage
    all_chats = localS.getItem("all_chats")
    if not all_chats: all_chats = {}
    
    # Create and add the new chat
    all_chats[new_chat_name] = []
    st.session_state.current_chat_id = new_chat_name
    st.session_state.messages = []
    
    # Save the updated list to local storage
    localS.setItem("all_chats", all_chats)
    
    # Navigate to the new chat page
    st.session_state.current_page = "chat_page"
    st.rerun()

def delete_current_chat():
    # Reload chats
    all_chats = localS.getItem("all_chats")
    
    # Remove the active chat
    if st.session_state.current_chat_id in all_chats:
        del all_chats[st.session_state.current_chat_id]
    
    # Ensure there's at least one chat, or go to homepage
    if len(all_chats) == 0:
        localS.setItem("all_chats", {})
        go_to_homepage()
    else:
        # Sort and pick the next most recent chat
        sorted_chat_names = sorted(all_chats.keys(), reverse=True)
        st.session_state.current_chat_id = sorted_chat_names[0]
        st.session_state.messages = all_chats[st.session_state.current_chat_id]
        localS.setItem("all_chats", all_chats)
        st.rerun()

def switch_chat(new_chat_name):
    # Reload chats
    all_chats = localS.getItem("all_chats")
    
    if new_chat_name in all_chats:
        st.session_state.current_chat_id = new_chat_name
        st.session_state.messages = all_chats[new_chat_name]
        st.rerun()

def continue_last_chat():
    # Reload chats
    all_chats = localS.getItem("all_chats")
    
    if not all_chats:
        start_new_chat() # No chats exist, start one
    else:
        # Navigate to the first chat found (implied "most recent")
        st.session_state.current_chat_id = list(all_chats.keys())[0]
        st.session_state.messages = all_chats[st.session_state.current_chat_id]
        st.session_state.current_page = "chat_page"
        st.rerun()

# --- INITIALIZE STATE ON FIRST LOAD ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "homepage"
    st.session_state.current_chat_id = None
    st.session_state.messages = []

# ==========================================
# ============ BRANCH: HOMEPAGE ============
# ==========================================
if st.session_state.current_page == "homepage":
    # 1. Inject abstract background elements
    st.markdown('<div class="homepage-wrapper"><div class="abstract-background"></div></div>', unsafe_allow_html=True)
    
    # 2. Homepage content layout
    with st.container():
        st.markdown('<div class="homepage-content">', unsafe_allow_html=True)
        st.markdown('<div class="homepage-header">Let\'s Chat</div>', unsafe_allow_html=True)
        st.markdown('<div class="homepage-tagline">Welcome back. Start a new conversation or pick up where you left off.</div>', unsafe_allow_html=True)
        
        # 3. Homepage primary action buttons
        col1, col2 = st.columns(2)
        with st.markdown('<div class="homepage-buttons">', unsafe_allow_html=True):
            with col1:
                st.button("➕ New Chat", use_container_width=True, on_click=start_new_chat)
            with col2:
                # Disable the button if no chats exist
                # all_chats = localS.getItem("all_chats") # Removed due to component constraint
                # disable_continue = not (all_chats and len(all_chats) > 0)
                # Instead, check if chat_id exists in session state from previous visits.
                # If no chat ID, they must create a new chat first.
                disable_continue = st.session_state.current_chat_id is None
                st.button("🔄 Continue Chat", use_container_width=True, on_click=continue_last_chat, disabled=disable_continue)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ============ BRANCH: CHAT PAGE ============
# ==========================================
else:
    # Reload chats from local storage for current state
    all_chats = localS.getItem("all_chats")
    if not all_chats: all_chats = {} # Fallback
    
    # --- SIDEBAR CONROLS ---
    with st.sidebar:
        # Home navigation and Title
        st.title("⚙️ Controls")
        
        # 1. Floating combined controls section
        st.markdown('<div class="controls-container">', unsafe_allow_html=True)
        cols_ctrl = st.columns(2)
        with cols_ctrl[0]:
            st.button("➕ New Chat", use_container_width=True, on_click=start_new_chat)
        with cols_ctrl[1]:
            st.button("🗑️ Delete Chat", use_container_width=True, on_click=delete_current_chat)
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # 2. AI Model Selection dropdown
        selected_model = st.selectbox(
            "🧠 Choose AI Model",
            ["gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-3-flash-preview"],
            # Ensure index matches previous state if possible, default to first item
            index=["gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-3-flash-preview"].index(getattr(st.session_state, 'active_model', 'gemini-2.5-flash'))
        )
        st.session_state.active_model = selected_model # Store model in state

        st.divider()

        # 3. Custom Chat Selection List (Highlighted box style)
        st.subheader("📝 Recent Chats")
        
        if all_chats:
            # Sort chats by key (which are time-based in this code) in descending order
            sorted_chat_names = sorted(all_chats.keys(), reverse=True)
            for chat_name in sorted_chat_names:
                # Is this the currently active chat? Disable the button to highlight it.
                is_active = chat_name == st.session_state.current_chat_id
                
                # Render as a button with a highlight effect applied by CSS if it is disabled
                st.button(
                    chat_name,
                    key=f"chat_{chat_name}",
                    on_click=switch_chat, 
                    args=(chat_name,),
                    use_container_width=True,
                    disabled=is_active
                )
        else:
            st.caption("No chats found.")

    # --- MAIN PAGE CHAT VIEW ---
    st.title(f"{st.session_state.current_chat_id} ✨")
    avatars = {"user": "🧑‍💻", "assistant": "🤖"}

    # Display the conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=avatars[message["role"]]):
            st.markdown(message["content"])

    # --- AI SETUP ---
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(getattr(st.session_state, 'active_model', 'gemini-2.5-flash'))

    # --- CHAT INPUT & LOGIC ---
    if user_prompt := st.chat_input("Message your AI..."):
        
        # 1. Display and save user message
        st.chat_message("user", avatar=avatars["user"]).markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        # 2. INTERCEPT SECRET CODE FEATURE
        # Force a response for exact "143" trigger
        if user_prompt.strip() == "143":
            custom_response = "Hey darling, your husband here! just wanted to let you know that im so proud of you, and I really really love you so much and I forever will! heheheh, I love you so much my pretty girl!" # Replace this with your exact message.
            with st.chat_message("assistant", avatar=avatars["assistant"]):
                st.markdown(custom_response)
            
            # Save the custom response to session memory
            st.session_state.messages.append({"role": "assistant", "content": custom_response})
            
        else:
            # Normal AI execution
            with st.chat_message("assistant", avatar=avatars["assistant"]):
                with st.spinner("🤖 Thinking..."):
                    # Call Gemini API
                    try:
                        response = model.generate_content(user_prompt)
                        st.markdown(response.text)
                        
                        # Save AI Response to session memory
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Error calling API: {str(e)}")

        # 3. Save the updated chat history to local storage
        # Load latest chats again to merge and save
        all_chats_update = localS.getItem("all_chats")
        if not all_chats_update: all_chats_update = {}
        all_chats_update[st.session_state.current_chat_id] = st.session_state.messages
        localS.setItem("all_chats", all_chats_update)
