import requests
print("Loaded ollama_client:", __file__)

def ollama_chat(system_prompt: str, user_prompt: str, model="gemma3:4b"):
    url = "http://127.0.0.1:11434/api/generate"

    # Create a combined prompt manually (since /api/chat is not available)
    full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"

    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False
    }

    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json().get("response", "")


if __name__ == "__main__":
    system_prompt = "You are a testing assistant."
    user_prompt = "Reply with a short hello."

    reply = ollama_chat(system_prompt, user_prompt)
    print("\n📝 Ollama Reply:\n", reply)