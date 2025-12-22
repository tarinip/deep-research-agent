# import requests
# #print("Loaded ollama_client:", __file__)

# def ollama_chat(system_prompt: str, user_prompt: str, model="gemma3:4b"):
#     url = "http://127.0.0.1:11434/api/generate"

#     # Create a combined prompt manually (since /api/chat is not available)
#     full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"

#     payload = {
#         "model": model,
#         "prompt": full_prompt,
#         "stream": False
#     }

#     r = requests.post(url, json=payload)
#     r.raise_for_status()
#     return r.json().get("response", "")


# import requests

# def ollama_chat(model="gemma3:4b", messages=None, system_prompt=None, user_prompt=None):
#     url = "http://127.0.0.1:11434/api/generate"
    
#     # 1. Handle the 'messages' format (preferred for chat/graph tasks)
#     if messages:
#         payload_messages = messages
#     else:
#         # 2. Fallback for your manual system/user prompt logic
#         payload_messages = []
#         if system_prompt:
#             payload_messages.append({"role": "system", "content": system_prompt})
#         if user_prompt:
#             payload_messages.append({"role": "user", "content": user_prompt})

#     payload = {
#         "model": model,
#         "messages": payload_messages,
#         "stream": False
#     }

#     r = requests.post(url, json=payload)
#     r.raise_for_status()
    
#     # The response structure for /api/chat is different (nested in 'message')
#     return r.json().get("message", {}).get("content", "")
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
load_dotenv()
def chat_with_llm(system_prompt: str, user_prompt: str, model="gpt-4o-mini"):
    """
    Uses LangChain and OpenAI to generate a response.
    """
    # 1. Initialize the Chat Model
    # It automatically looks for the OPENAI_API_KEY environment variable
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1  # Set low for factual research/summarization
    )

    # 2. Format the messages using LangChain's message objects
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    try:
        # 3. Invoke the model
        response = llm.invoke(messages)
        
        # 4. Return just the text content
        return response.content
    except Exception as e:
        print(f"❌ OpenAI/LangChain Error: {e}")
        return ""

# # Example usage:
# result = chat_with_llm("You are a helpful assistant", "What is LangGraph?")
# print(result)