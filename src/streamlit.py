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
    page_title="Balance Bites",
    page_icon="./data/logo.png"
)

image = Image.open("./data/logo.png")

st.sidebar.image(image,use_column_width="always")

st.title("_Balance Bites_ :apple:")

# header
st.header("Las recetas que más te gustan con el apoyo que necesitas")

# Initialize chat history and create starting message
if "messages" not in st.session_state:
    st.session_state.messages = []

    assistant_initial_message = random.choice(
        [
            "Hola! Soy BB. ¿En qué te puedo ayudar?",
            "Me puedes llamar BB. ¿Tienes alguna pregunta para mi?",
            "¡Hola! Soy BB, tu asistente virtual especializado en dietas. ¿Cómo puedo ayudarte hoy?",
            "Bienvenido, estoy aquí para ayudarte con todas tus dudas sobre dietas. ¿En qué puedo asistirte hoy?",
            "¡Hola! Soy BB, tu compañero para resolver todas tus preguntas sobre dietas. ¿Qué información necesitas?",
        ]
    )

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_initial_message}
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message(message["role"],avatar="🍎"):
            st.markdown(message["content"])
    else:
        with st.chat_message(message["role"],avatar="👤"):
            st.markdown(message["content"])
        

# Buttons side by side using st.columns
button1_col, button2_col, button3_col = st.columns(3)

with button1_col:
    button1_clicked = st.button('Plan semanal', help="Pulsa aquí si quieres tu plan semanal personalizado de comidas.")
with button2_col:
    button2_clicked = st.button('Motivación', help="Pulsa aquí si necesitas motivación con tu dieta.")
with button3_col:
    button3_clicked = st.button('Háblame', help="Pulsa aquí si quieres que el chat te lea los mensajes.")

# Check if buttons are clicked
if button1_clicked:
    st.write("Button 1 clicked!")
if button2_clicked:
    st.write("Button 2 clicked!")
if button3_clicked:
    st.write("Button 3 clicked!")


# Accept user input
if prompt := st.chat_input("Puedo ayudarte en algo?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user",avatar="👤"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant",avatar="🍎"):
        message_placeholder = st.empty()
        response = chain.predict(user_prompt=prompt)
        st.session_state.chain_messages = chain.memory.chat_memory.messages

        message_placeholder.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})