import os
import ctypes
import subprocess
from typing_extensions import Annotated
from pydantic import Field
from agents import function_tool


@function_tool
def system_control(
    action: Annotated[
        str,
        Field(
            description="System action to perform. Options: 'volume_up', 'volume_down', 'mute', 'brightness_up', 'brightness_down', 'shutdown', 'restart', 'lock'",
            json_schema_extra={"type": "string"},
        ),
    ]
) -> str:
    """
    Perform system control actions like volume, brightness, shutdown, restart, or lock.
    """

    try:
        if action == "volume_up":
            # Increase volume by 2 units
            os.system("nircmd.exe changesysvolume 2000")
            return "🔊 Volume increased."

        elif action == "volume_down":
            os.system("nircmd.exe changesysvolume -2000")
            return "🔉 Volume decreased."

        elif action == "mute":
            os.system("nircmd.exe mutesysvolume 2")
            return "🔇 Volume muted/unmuted."

        elif action == "brightness_up":
            subprocess.run("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)", shell=True)
            return "☀️ Brightness set to 100%."

        elif action == "brightness_down":
            subprocess.run("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,10)", shell=True)
            return "🌙 Brightness set to 10%."

        elif action == "shutdown":
            os.system("shutdown /s /t 0")
            return "💻 Shutting down the system..."

        elif action == "restart":
            os.system("shutdown /r /t 0")
            return "🔄 Restarting the system..."

        elif action == "lock":
            ctypes.windll.user32.LockWorkStation()
            return "🔒 System locked."

        else:
            return f"⚠️ Unknown action: {action}"

    except Exception as e:
        return f"❌ Error performing action: {e}"

