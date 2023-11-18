import os
import streamlit as st
import random
from PIL import Image
import sys
from text2speech2text import text_to_speech_azure
from streamlit_mic_recorder import speech_to_text

azure_key = os.environ["AZURESPEECH_API_KEY"]

def chat_response(prompt,show_promt=True):
    if show_promt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user",avatar="👤"):
            st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant",avatar="🍎"):
        message_placeholder = st.empty()
        response = agent_execute(agent, prompt)
        st.session_state.chain_messages = agent.memory.chat_memory.messages
        
        message_placeholder.markdown(response)
        if togg:
            text_to_speech_azure(response, region="westeurope", key=azure_key)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

sys.path.append(os.getcwd())
from src.agent import get_agent, agent_execute

# Start farmer partner agent
agent = get_agent()
if "chain_messages" in st.session_state:
    agent.memory.chat_memory.messages = st.session_state.chain_messages

st.set_page_config(
    page_title="Balance Bites",
    page_icon="./data/logo.png"
)

image = Image.open("./data/logo.png")

st.sidebar.image(image,use_column_width="always")

st.title("_Balance Bites_ :apple:")

# header
st.header("Las recetas que más te gustan, con el apoyo que necesitas")

# Buttons side by side using st.columns
button1_col, button2_col = st.columns(2)

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
        
with button1_col:
    button1_clicked = st.button('Plan semanal', help="Pulsa aquí si quieres tu plan semanal personalizado de comidas.")
with button2_col:
    button2_clicked = st.button('Motivación', help="Pulsa aquí si necesitas motivación con tu dieta.")

togg = st.sidebar.toggle('Usar Audio y Voz', help="Activa esta opción si quieres usar tu voz y que el chat te lea los mensajes.")
if togg:
    with st.sidebar:
        listened_text=speech_to_text(start_prompt="🎙️",stop_prompt="⏹️",language='es',use_container_width=True,just_once=True)

# Check if buttons are clicked
if button1_clicked:
    prompt = "Haz un plan semanal basado en la información que tienes de mi dieta hasta el momento."
    chat_response(prompt,show_promt=False)

if button2_clicked:
    # Add user message to chat history
    prompt = "Me siento falto de ánimos para seguir con mi dieta, por favor, anímame."
    chat_response(prompt,show_promt=False)

try:
    if listened_text:
       chat_response(listened_text)
except:
    pass

# Accept user input
if prompt := st.chat_input("Puedo ayudarte en algo?"):
    chat_response(prompt)
