import edge_tts
import os

AUDIO_DIR = "audio_output"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

async def convert_text_to_audio(text: str, filename: str) -> str:
    file_path = os.path.join(AUDIO_DIR, filename)

    voice = "en-US-AriaNeural"  # You can change the voice as needed

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)

    return file_path