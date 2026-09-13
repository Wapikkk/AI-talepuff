import edge_tts
import os

AUDIO_DIR = "audio_output"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

VOICE_MAPPING = {
    "Warm": "en-US-JennyNeural", 
    "Brave": "en-US-ChristopherNeural",
    "Gentle": "en-US-AriaNeural",
    "Character": "en-US-EricNeural",
    "Friendly": "en-US-GuyNeural",
    "Neutral": "en-US-SteffanNeural"
}

async def convert_text_to_audio(text: str, voice_tone: str, filename: str) -> str:
    file_path = os.path.join(AUDIO_DIR, filename)

    voice = VOICE_MAPPING.get(voice_tone, "en-US-AriaNeural")

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)

    return file_path