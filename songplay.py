import pywhatkit
from agents import function_tool

@function_tool
def play_youtube(song_name: str) -> str:
    """
    Play a song or video on YouTube by searching its name.
    
    Args:
        song_name (str): The name of the song or video to play.
    
    Returns:
        str: Confirmation message.
    """
    try:
        pywhatkit.playonyt(song_name)  # Opens YouTube in browser and plays
        return f"Playing '{song_name}' on YouTube..."
    except Exception as e:
        return f"Failed to play '{song_name}'. Error: {str(e)}"

