import requests

def generate_story_from_ollama(category: str, sentiment: str) -> str:
    prompt_text = {
        f"Buatkan cerita anak maksimal 3 paragraf bertema {category} dengan suasana {sentiment}."
        "Strict rules: "
        "1. Only use CEFR A1 English Beginner Vocabulary"
    }
    payload = {
        "model": "qwen:0.5b",
        "prompt": prompt_text,
        "stream": False,
    }

    response = requests.post("http://localhost:11434/api/generate", json=payload)
    response.raise_for_status()
    return response.json().get("response", "")