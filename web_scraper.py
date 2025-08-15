import trafilatura
import logging

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results is not directly readable, better to be summarized by LLM before consume
    by the user.

    Some common website to crawl information from:
    MLB scores: https://www.mlb.com/scores/YYYY-MM-DD
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            raise Exception("Failed to fetch content from URL")
        
        # Extract text content
        text = trafilatura.extract(downloaded)
        
        if not text:
            raise Exception("No text content could be extracted")
        
        return text
        
    except Exception as e:
        logging.error(f"Error in get_website_text_content: {str(e)}")
        raise Exception(f"Failed to extract content: {str(e)}")
