import wikipediaapi
from agents import function_tool

@function_tool
def search_wikipedia(query: str, language: str = "en") -> str:
    """
    Search Wikipedia and return a summary of the page if it exists.
    
    Args:
        query (str): The topic to search for.
        language (str): The Wikipedia language edition (default: "en").
    
    Returns:
        str: Summary of the page or an error message.
    """
    user_agent = "TalhaSearch/1.0 (https://www.linkedin.com/in/talha-umar-38697937b; talhaumar097@gmail.com)" # <-- Replace with your info
    wiki = wikipediaapi.Wikipedia(
        language=language,
        user_agent=user_agent
    )
    
    page = wiki.page(query)
    if not page.exists():
        return "No page found."
    
    return page.summary[:1000]  # return first 1000 chars

