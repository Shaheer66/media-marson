import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def get_supabase_client() -> Client:
    """Initializes and returns a Supabase client."""
    url: Optional[str] = os.environ.get("SUPABASE_URL")
    key: Optional[str] = os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        logger.error("Supabase credentials missing in .env")
        raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY")
        
    return create_client(url, key)

def configure_gemini() -> None:
    """Configures the Gemini SDK."""
    api_key: Optional[str] = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("Gemini API Key missing in .env")
        raise ValueError("Missing GEMINI_API_KEY")
    
    genai.configure(api_key=api_key)

def get_gemini_model(model_name: str = "gemini-1.5-flash") -> genai.GenerativeModel:
    """Returns a configured Gemini model instance."""
    configure_gemini()
    return genai.GenerativeModel(model_name)

if __name__ == "__main__":
    try:
        sb = get_supabase_client()
        logger.info("Connection: Supabase is online.")
        
        model = get_gemini_model()
        logger.info(f"Connection: Gemini ({model.model_name}) is online.")
    except Exception as e:
        logger.critical(f"Production Check Failed: {e}")