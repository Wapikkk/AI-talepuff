import requests

def generate_story_from_ollama(category: str, sentiment: str) -> str:
    prompt_text = (
        f"Write a simple children's story about {category} with a {sentiment} mood."
        "Strict rules: "
        "1. Only use CEFR A1 English Beginner Vocabulary"
        "2. Keep sentences short and simple"
        "3. Maximum 3 shor paragraphs"
        "4. Do not use complex words"
    )
    payload = {
        "model": "qwen:0.5b",
        "prompt": prompt_text,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "repeat_penalty": 1.2,
        } 
    }

    response = requests.post("http://localhost:11434/api/generate", json=payload)
    response.raise_for_status()
    return response.json().get("response", "")