import pyaudio
import wave
import openai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Audio config
CHUNK = 1024  # buffer size
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper expects 16kHz
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

def record_audio():
    """Record audio from mic and save as wav file"""
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    
    print("🎙️ Listening... Speak now!")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("✅ Recording finished!")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio():
    """Send recorded audio to OpenAI Whisper and return text"""
    with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="gpt-4o-transcribe",  # Whisper v2
            file=audio_file
        )
    return transcript.text

# if __name__ == "__main__":
#     record_audio()
#     text = transcribe_audio()
#     print("📝 Transcription:", text)
