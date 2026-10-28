import edge_tts
import os
import subprocess

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

TICKS_PER_MS = 10_000  # edge-tts menghitung waktu dalam satuan 100 ns


def sentence_from_boundary(chunk: dict) -> dict:
    """Satu kalimat dengan waktu mulai/selesai dalam milidetik, dari penanda SentenceBoundary edge-tts."""
    start = int(chunk["offset"] // TICKS_PER_MS)
    end = start + int(chunk["duration"] // TICKS_PER_MS)
    return {"start": start, "end": end, "text": chunk["text"].strip()}


async def convert_text_to_audio(text: str, voice_tone: str, filename: str) -> tuple[str, list[dict]]:
    wav_filename = filename.replace('.mp3', '.wav')
    wav_path = os.path.join(AUDIO_DIR, wav_filename)
    mp3_path = os.path.join(AUDIO_DIR, filename)

    voice = VOICE_MAPPING.get(voice_tone, "en-US-JennyNeural")

    communicate = edge_tts.Communicate(text, voice, boundary="SentenceBoundary")
    sentences = []
    with open(mp3_path, "wb") as audio:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                sentences.append(sentence_from_boundary(chunk))

    command = [
        "ffmpeg", "-y", "-i", mp3_path,
        "-ac", "1", "-ar", "24000", wav_path
    ]

    try:
        subprocess.run(command, check=True, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error converting MP3 to WAV: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        if os.path.exists(mp3_path):
            os.remove(mp3_path)

    return wav_path, sentences
