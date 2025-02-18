from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

def google_search(query, num_results=10):
    """
    Performs a Google Search using the Custom Search API.
    Make sure to set your GOOGLE_API_KEY and GOOGLE_CSE_ID in environment variables.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        raise ValueError(
            "GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables must be set."
        )

    service = build("customsearch", "v1", developerKey=api_key)
    try:
      response = (
          service.cse()
          .list(q=query, cx=cse_id, num=num_results)
          .execute()
      )
      results = response.get("items", [])
      # Format results as a list of dictionaries with titles, links, and snippets
      formatted_results = [
          {"title": res['title'], "link": res['link'], "snippet": res['snippet']}
          for res in results
      ]
      return formatted_results

    except Exception as e:
        print(f"Error during google search: {e}")
        return f"Error during web search: {e}"