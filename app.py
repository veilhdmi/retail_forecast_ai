import os

import streamlit as st
from dotenv import load_dotenv

from agent import run_turn

load_dotenv()

for _key in ("ANTHROPIC_API_KEY", "GCP_PROJECT", "GOOGLE_CREDENTIALS_JSON"):
    if _key in st.secrets:
        os.environ[_key] = st.secrets[_key]

st.set_page_config(page_title="Stock Planner AI", page_icon="📦")

if "api_messages" not in st.session_state:
    st.session_state.api_messages = []
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

title_col, reset_col = st.columns([5, 1])
with title_col:
    st.title("📦 Stock Planner")
    st.caption("Chat with your sales and inventory data (BigQuery + Claude).")
with reset_col:
    st.write("")
    if st.button("🔄 New chat", use_container_width=True):
        st.session_state.api_messages = []
        st.session_state.display_messages = []
        st.rerun()

if not st.session_state.display_messages:
    st.info("💡 Try: *\"which categories are at risk of running out of stock?\"*")

for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        if msg.get("tools_used"):
            st.caption(f"🔧 Queried: {', '.join(msg['tools_used'])}")
        st.write(msg["text"])

question = st.chat_input("Ask something about your inventory...")

if question:
    st.session_state.display_messages.append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.write(question)

    st.session_state.api_messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            updated_messages, reply, tools_used = run_turn(st.session_state.api_messages)
        st.session_state.api_messages = updated_messages
        if tools_used:
            st.caption(f"🔧 Queried: {', '.join(tools_used)}")
        st.write(reply)

    st.session_state.display_messages.append({
        "role": "assistant",
        "text": reply,
        "tools_used": tools_used,
    })
