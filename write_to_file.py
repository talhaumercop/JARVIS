from agents import function_tool

@function_tool
def write_to_file(file_path: str, text: str) -> None:
    """
    Write the given text into a file at the specified path.
    If the file exists, it will be overwritten.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Successfully wrote text to {file_path}")
    except Exception as e:
        print(f"❌ Error writing to file: {e}")

# write_to_file("C:/Users/talha/Desktop/test.txt", "Hello Aether, writing into files 🚀")
