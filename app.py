import streamlit as st
import google.generativeai as genai

# 1. Set up the page appearance
st.set_page_config(page_title="My Custom AI", page_icon="🤖")
st.title("Welcome to My Gemini Chatbot! 🚀")

# 2. Securely load your API Key
# We use st.secrets so your key isn't public when you share the code
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Initialize the Gemini Model
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Set up the chat history memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages so the screen doesn't clear every time you type
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. The Chat Input Box
if user_prompt := st.chat_input("Ask me anything..."):
    
    # Show what the user typed on the screen and save it to history
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Send the prompt to Gemini and get the response
    response = model.generate_content(user_prompt)

    # Show Gemini's response on the screen and save it to history
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})