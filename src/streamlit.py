import os
import streamlit as st
import random
from PIL import Image
import sys

sys.path.append(os.getcwd())
from src.agent import get_chain

# Start farmer partner agent
chain = get_chain()
if "chain_messages" in st.session_state:
    chain.memory.chat_memory.messages = st.session_state.chain_messages

st.set_page_config(
    page_title="Endless Innovators",
)

st.title("Endless Innovators")

# Initialize chat history and create starting message
if "messages" not in st.session_state:
    st.session_state.messages = []

    assistant_initial_message = random.choice(
        [
            "Hola! Soy X. ¿En qué te puedo ayudar?",
            "Me puedes llamar X. ¿Tienes alguna pregunta para mi?",
            "¡Hola! Soy X, tu asistente virtual especializado en dietas. ¿Cómo puedo ayudarte hoy?",
            "Bienvenido, estoy aquí para ayudarte con todas tus dudas sobre dietas. ¿En qué puedo asistirte hoy?",
            "¡Hola! Soy X, tu compañero para resolver todas tus preguntas sobre dietas. ¿Qué información necesitas?",
        ]
    )

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_initial_message}
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Puedo ayudarte en algo?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = chain.predict(user_prompt=prompt)
        st.session_state.chain_messages = chain.memory.chat_memory.messages

        message_placeholder.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})