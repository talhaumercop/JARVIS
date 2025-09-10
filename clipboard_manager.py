import pyperclip
from agents import function_tool

# Simple clipboard history
clipboard_history = []

@function_tool
def save_clipboard():
    """Save current clipboard content to history."""
    text = pyperclip.paste()
    if text and (not clipboard_history or clipboard_history[-1] != text):
        clipboard_history.append(text)
        print(f"✅ Saved to history: {text[:50]}...")  # show only first 50 chars
    else:
        print("⚠️ Clipboard empty or already saved.")

@function_tool
def get_clipboard_history():
    """Return the clipboard history."""
    return clipboard_history

@function_tool
def get_last_clipboard():
    """Return the last item in clipboard history."""
    return clipboard_history[-1] if clipboard_history else None
