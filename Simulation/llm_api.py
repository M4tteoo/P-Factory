import requests

def call_local_llm(prompt, model="mistral"):
    """
    Calls a local LLM served by Ollama.
    
    Args:
        prompt (str): The user prompt containing agent traits, goal, and dialogue.
        model (str): The model name (e.g., 'mistral', 'phi3', etc.).

    Returns:
        str: The generated response from the LLM.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a character in a simulation. Stay in character and speak naturally."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.6,
                "stream": False
            }
        )
        data = response.json()
        return data["message"]["content"].strip()

    except Exception as e:
        print(f"Error calling local LLM: {e}")
        return "[Failed to respond]"

# This code will only run if you execute `python llm_api.py` directly
if __name__ == "__main__":
    print("Testing LLM API call...")
    response = call_local_llm("What's the capital of Italy?")
    print(f"LLM Response: {response}")