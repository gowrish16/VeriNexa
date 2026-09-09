import requests
import json

def query_ollama(prompt, model="llama3.1:8b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

if __name__ == "__main__":
    result = query_ollama("Say hello in exactly one sentence.")
    print(result)