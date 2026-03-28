import os
from groq import Groq
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_compound_research(chapter_title: str, book_title: str) -> str:
    """
    Uses Groq's Compound Mini to natively search the web and extract facts.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # We just ask it to search. The model handles the tool calling automatically.
    prompt = f"Search the web for 5 verified, up-to-date facts about '{chapter_title}' for the book '{book_title}'. Return only the facts and sources."

    try:
        completion = client.chat.completions.create(
            model="groq/compound-mini", 
            messages=[
                {"role": "system", "content": "You are a research assistant. Use your built-in web search to find factual data."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Compound Mini Research Failed: {e}")
        return "Research failed. Proceeding with internal knowledge."