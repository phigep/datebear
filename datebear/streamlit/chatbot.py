import streamlit as st
import numpy as np
import random
import time
import requests
import os
import json

headers = {
    'Content-Type': 'application/json',
    # 'Authorization': 'Bearer your_token_here'  # if the API requires authentication
}

st.set_page_config(page_title="Dattelbot", page_icon="../data/datebear.ico", layout="wide")

# Logo einfügen
image_path = os.path.join("..", "data", "datebear.png")

st.image(image_path, width=200)

st.title("Dattelbot - Dattelbär Chatbot")
st.write("Dattel? Bär.")

# colors ändern

# set API path to interact with API
API_URL = "http://127.0.0.1:8000"
# create chat history
if "messages" not in st.session_state:
    init_res = requests.get(f"{API_URL}/initchat")
    if init_res.status_code == 200:
        st.session_state.chat_messages = init_res.json().get("messages", "")
    st.session_state.messages = []
        
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["content"])

def response_generator(messages):
    response = requests.post(f"{API_URL}/chatpost", json={"messages": messages},headers=headers)
    print(response.content)
    if response.status_code == 200:
        #answer = response.json().get("answer", "")
        st.session_state.chat_messages = response.json().get("messages", "")["messages"]
        yield st.session_state.chat_messages[-1]["content"]
    else:
        st.write("Fehler bei der Anfrage. Bitte versuche es erneut.")

if prompt := st.chat_input("Stelle mir eine Frage!"):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    print("session state message object: ",st.session_state.chat_messages)
    st.session_state.messages.append({"role": "user", "avatar": "👤", "content": prompt})
    st.session_state.chat_messages.append({"role": "user", "content": prompt})


    with st.chat_message("assistant", avatar="🐻"):
        response_content = st.write_stream(response_generator(st.session_state.chat_messages))
    st.session_state.messages.append({"role": "assistant", "avatar": "🐻", "content": response_content})
    st.session_state.chat_messages.append({"role": "user", "content": response_content})






