import requests

def generate_story_from_ollama(
        character_name: str,
        theme: str,
        mood: str,
        length_minutes: int,
        language: str,
        description: str,
) -> str:
    target_words = length_minutes * 100
    prompt_text = (
        "System: You are an expert children's book author specializing in stories for toddlers (ages 2-4). "
        "Strictly follow these rules:\n"
        "1. Only use CEFR A1 English Beginner Vocabulary and simple grammar (mostly present tense).\n"
        "2. Keep sentences short and simple and use gentle word repetition.\n"
        "3. Keep the conflict very mild and strictly avoid any scary or complex themes.\n"
        "4. You MUST output the response in this EXACT format:\n"
        "TITLE: [Write the story title here]\n"
        "CONTENT: [Write the story text here]\n"
        "Do not include any conversational filler.\n\n"
        f"User: Please write a story using the following specifications:\n"
        f"- Main Character Name: {character_name}\n"
        f"- Theme: {theme}\n"
        f"- Mood/Tone: {mood}\n"
        f"- Language: {language}\n"
        f"- Length: closely around {target_words} words\n\n"
        f"Story Concept:\n\"{description}\""
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
    raw_output = response.json().get("response", "")
    
    title = f"{character_name}'s Adventure"
    content = raw_output
    
    if "TITLE:" in raw_output and "CONTENT:" in raw_output:
        parts = raw_output.split("CONTENT:")
        title = parts[0].replace("TITLE:", "").strip()
        content = parts[1].strip()
        
    return title, content