import asyncio
import os
import subprocess

import aiohttp
import edge_tts

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


SYNTHESIS_ATTEMPTS = 3
SYNTHESIS_RETRY_DELAY = 1.0  # detik

# Gangguan sambungan ke layanan Microsoft (hotspot, Wi-Fi umum) biasanya sesaat; mencoba lagi sering cukup.
_TRANSIENT = (aiohttp.ClientError, asyncio.TimeoutError, OSError, edge_tts.exceptions.EdgeTTSException)


async def _synthesize(text: str, voice: str, mp3_path: str) -> list[dict]:
    last_error: Exception | None = None
    for attempt in range(1, SYNTHESIS_ATTEMPTS + 1):
        sentences: list[dict] = []
        try:
            communicate = edge_tts.Communicate(text, voice, boundary="SentenceBoundary")
            with open(mp3_path, "wb") as audio:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio.write(chunk["data"])
                    elif chunk["type"] == "SentenceBoundary":
                        sentences.append(sentence_from_boundary(chunk))
            return sentences
        except _TRANSIENT as e:
            last_error = e
            print(f"TTS attempt {attempt}/{SYNTHESIS_ATTEMPTS} failed: {e}")
            if attempt < SYNTHESIS_ATTEMPTS:
                await asyncio.sleep(SYNTHESIS_RETRY_DELAY)
    raise last_error


async def convert_text_to_audio(text: str, voice_tone: str, filename: str) -> tuple[str, list[dict]]:
    wav_filename = filename.replace('.mp3', '.wav')
    wav_path = os.path.join(AUDIO_DIR, wav_filename)
    mp3_path = os.path.join(AUDIO_DIR, filename)

    voice = VOICE_MAPPING.get(voice_tone, "en-US-JennyNeural")

    sentences = await _synthesize(text, voice, mp3_path)

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
