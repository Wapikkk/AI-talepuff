import edge_tts
import os
import io
from pydub import AudioSegment

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
    final_filename = filename.replace('.mp3', '.wav')
    file_path = os.path.join(AUDIO_DIR, final_filename)

    voice = VOICE_MAPPING.get(voice_tone, "en-US-JennyNeural")

    communicate = edge_tts.Communicate(text, voice)

    mp3_memory = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_memory.write(chunk["data"])

    mp3_memory.seek(0)

    audio = AudioSegment.from_file(mp3_memory, format="mp3")
    audio = audio.set_channels(1).set_frame_rate(24000)

    audio.export(file_path, format="wav")

    return file_path