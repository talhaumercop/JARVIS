import pyttsx3

def text_to_speech(text: str) -> None:
    """
    Convert input text to speech and play the audio.
    """
    try:
        engine = pyttsx3.init()
        # voices = engine.getProperty("voices")
        # engine.setProperty("voice", voices[1].id)
        engine.say(text)
        engine.runAndWait()
        print("✅ Finished speaking.")
    except Exception as e:
        print(f"❌ Error in TTS: {e}")
