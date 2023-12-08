# **
import streamlit as st
import time 
import os
import openai
import streamlit as st
from streamlit_chat import message
import backoff
import tiktoken

st.set_page_config(
    page_title="GPT4 ChatBot",
    page_icon=":robot:"
)

st.markdown("""
                <html>
                    <head>
                    <style>
                        section.main[tabindex="0"] {
                            overflow : scroll
                        }
                    </style>
                    </head>
                    <body>
                    </body>
                </html>
            """, unsafe_allow_html=True)


st.header("GPT4 ChatBot")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


def chatgpt(messages):
    if num_tokens_from_messages(messages,"gpt-4") > 8000:
        messages = messages[-2:]
        print("Found higher number of tokens  !!")
        print("Reprint message ::")
        print(*messages, sep = "\n")
    if num_tokens_from_messages(messages,"gpt-4") > 8000:
        messages = messages[-1:]
        print("Found higher number of tokens 2nd time also !!")
        print("Reprinting the message ::")
        print(*messages, sep = "\n")
        
    completion = openai.ChatCompletion.create(
      model="gpt-4", 
      messages=messages)
    print(f"token {completion['usage']}")
    return(completion['choices'][0]["message"]["content"])

def openapi_key_present():
    if 'openapikey' in st.session_state:
        if st.session_state['openapikey'] != "":
            return True
    return False

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


openai.api_key = st.text_input("API Key",key="api_key", type="password", disabled=openapi_key_present())
st.session_state['openapikey'] = openai.api_key
if openapi_key_present():
    user_input = st.text_area("You: ", "Hi", key="input")
    search_button = st.button("Search")

    if search_button and user_input and user_input != "" and user_input != "Hi":    
        pp = f'Answer the Question: {user_input}'
        messages = [{'role': 'system', 'content': 'You are an expert coder, who works with TypeScript'}]

        if st.session_state['generated']:
            for i in range(len(st.session_state['past'])-2, len(st.session_state['past'])):
                if i >= 0:
                    messages.append({'role': 'user', 'content': st.session_state['past'][i]})
                    messages.append({'role': 'assistant', 'content': st.session_state['generated'][i]})
            messages.append({'role': 'user', 'content': pp})
        else:
            messages = [{'role': 'user', 'content': pp}]

        try:
            answer = chatgpt(messages)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(answer)
        except Exception as e:
            st.error(str(e))

    elif user_input == "Hi":
        st.session_state.past.append("Hi")
        st.session_state.generated.append("Hi, I am a GPT-4 Chat Bot. Ask me anything")

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

