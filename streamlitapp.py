import streamlit as st
import requests
import datetime

# from exception.exceptions import TradingBotException
import sys

BASE_URL = "https://aitravel-planner-gy4l.onrender.com/"  

st.set_page_config(
    page_title="🌍 Travel Planner Agentic Application",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🌍 Travel Planner Agentic Application")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
st.header("How can I help you in planning a trip? Let me know where do you want to visit.")

# Show full chat history in a chat-like format
if st.session_state.messages:
    st.subheader("Chat History")
    for msg in st.session_state.messages:
        if msg.startswith("User:"):
            st.markdown(f"<div style='color:blue'><b>{msg}</b></div>", unsafe_allow_html=True)
        elif msg.startswith("Assistant:"):
            st.markdown(f"<div style='color:green'><b>{msg}</b></div>", unsafe_allow_html=True)
        else:
            st.markdown(msg)

# Chat input box at bottom
with st.form(key="query_form", clear_on_submit=True):
    user_input = st.text_input("User Input", placeholder="e.g. Plan a trip to Goa for 5 days")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input.strip():
    try:
        # Append user message to chat history
        st.session_state.messages.append(f"User: {user_input}")
        with st.spinner("Bot is thinking..."):
            # Send the full chat history (as plain strings) to the backend
            payload = {"messages": st.session_state.messages}
            response = requests.post(f"{BASE_URL}/query", json=payload)
        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")
            # Append assistant response to chat history
            st.session_state.messages.append(f"Assistant: {answer}")
            markdown_content = f"""# 🌍 AI Travel Plan\n\n# **Generated:** {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')}  \n# **Created by:** Atriyo's Travel Agent\n\n---\n\n{answer}\n\n---\n\n*This travel plan was generated by AI. Please verify all information, especially prices, operating hours, and travel requirements before your trip.*\n"""
            st.markdown(markdown_content)
        else:
            st.error(" Bot failed to respond: " + response.text)
    except Exception as e:
      raise Exception(f"The response failed due to {e}")
