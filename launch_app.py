import os
from agents import function_tool
import subprocess

@function_tool
def launch_app(app_name: str):
    """
    Launches an application by name.
    Works for apps in PATH (like chrome, code) or full exe paths.
    """
    try:
        # Try using 'start' for apps in PATH
        subprocess.Popen(["start", app_name], shell=True)
        print(f"✅ Launching {app_name}...")
    except Exception as e:
        print(f"❌ Could not launch {app_name}: {e}")

