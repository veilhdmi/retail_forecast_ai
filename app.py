import streamlit as st
from dotenv import load_dotenv

from agent import run_turn

load_dotenv()

st.set_page_config(page_title="Stock Planner AI", page_icon="📦")

if "api_messages" not in st.session_state:
    st.session_state.api_messages = []
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

title_col, reset_col = st.columns([5, 1])
with title_col:
    st.title("📦 Stock Planner")
    st.caption("Chatea con tus datos de ventas e inventario (BigQuery + Claude).")
with reset_col:
    st.write("")
    if st.button("🔄 Nuevo chat", use_container_width=True):
        st.session_state.api_messages = []
        st.session_state.display_messages = []
        st.rerun()

if not st.session_state.display_messages:
    st.info("💡 Prueba con: *\"¿qué categorías están en riesgo de quiebre de stock?\"*")

for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        if msg.get("tools_used"):
            st.caption(f"🔧 Consultó: {', '.join(msg['tools_used'])}")
        st.write(msg["text"])

question = st.chat_input("Pregúntale algo a tu inventario...")

if question:
    st.session_state.display_messages.append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.write(question)

    st.session_state.api_messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            updated_messages, reply, tools_used = run_turn(st.session_state.api_messages)
        st.session_state.api_messages = updated_messages
        if tools_used:
            st.caption(f"🔧 Consultó: {', '.join(tools_used)}")
        st.write(reply)

    st.session_state.display_messages.append({
        "role": "assistant",
        "text": reply,
        "tools_used": tools_used,
    })
