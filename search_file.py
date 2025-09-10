import os
from agents import function_tool


@function_tool
def search_file(filename: str, search_paths: list[str] | None = None) -> str | None:
    """
    Search for a file or folder by name in common directories.
    Returns the full path if found, otherwise None.
    """
    if search_paths is None:
        user = os.path.expanduser("~")
        search_paths = [
            os.path.join(user, "Desktop"),
            os.path.join(user, "Documents"),
            os.path.join(user, "Downloads"),
        ]

    for path in search_paths:
        for root, dirs, files in os.walk(path):
            if filename in files:
                return os.path.join(root, filename)
            if filename in dirs:
                return os.path.join(root, filename)

    return None
