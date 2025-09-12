import subprocess
from agents import function_tool


@function_tool
def run_command(command: str):
    """
    Run a command in PowerShell (or CMD) and return its output.
    """
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True
        )
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error: {e}"

