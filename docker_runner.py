import subprocess
import tempfile
import os
import uuid
from agents import function_tool

@function_tool
def run_code_in_docker(code: str, language: str = "python") -> str:
    """
    Runs the provided code inside a Docker container safely.
    
    Args:
        code (str): The code to execute.
        language (str): Programming language ('python' or 'node').
    
    Returns:
        str: Output or error message from execution.
    """
    # Map language to docker images
    docker_images = {
        "python": "python:3.11-slim",
        "node": "node:20-slim"
    }

    if language not in docker_images:
        return f"❌ Language {language} not supported."
    
    image = docker_images[language]

    # Create a temp directory for code
    temp_dir = tempfile.mkdtemp()
    file_id = str(uuid.uuid4())[:8]

    if language == "python":
        filename = os.path.join(temp_dir, f"script_{file_id}.py")
    elif language == "node":
        filename = os.path.join(temp_dir, f"script_{file_id}.js")

    # Write code to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    # Run inside docker
    try:
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{temp_dir}:/app",
            "-w", "/app",
            image,
            "python" if language == "python" else "node",
            os.path.basename(filename)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout if result.returncode == 0 else result.stderr

    except subprocess.TimeoutExpired:
        output = "❌ Execution timed out."
    except Exception as e:
        output = f"❌ Error: {e}"

    finally:
        # Cleanup temp files
        try:
            os.remove(filename)
            os.rmdir(temp_dir)
        except:
            pass

    return output.strip()


