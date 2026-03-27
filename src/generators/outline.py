import logging
from typing import Optional
from src.database.connection import get_supabase_client, get_gemini_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a professional book architect. Generate a highly structured 10-chapter outline based strictly on the provided title and notes. 
Output format requirements:
- Plain text or markdown.
- 10 distinct chapters.
- Each chapter must include a title and a precise 3-sentence description of the content to be covered.
- Do not include conversational filler.

Title: {title}
Notes: {notes}
"""

def generate_outline(book_id: str) -> bool:
    """
    Retrieves book context, generates an outline via LLM, and persists it to the database.
    """
    try:
        supabase = get_supabase_client()
        
        # 1. Fetch and Validate
        response = supabase.table("books").select("title, pre_outline_notes, status").eq("id", book_id).single().execute()
        
        if not response.data:
            logger.error(f"Execution halted: No record found for ID {book_id}")
            return False
            
        book = response.data
        if book.get("status") != "drafting_outline":
            logger.warning(f"Execution halted: Invalid state '{book.get('status')}' for ID {book_id}")
            return False

        title = book.get("title")
        notes = book.get("pre_outline_notes")
        
        if not title or not notes:
            logger.error("Execution halted: Missing mandatory fields (title or pre_outline_notes).")
            return False

        # 2. Generate Content
        logger.info(f"Initializing Gemini model for book: {title}")
        model = get_gemini_model()
        prompt = SYSTEM_PROMPT.format(title=title, notes=notes)
        
        llm_response = model.generate_content(prompt)
        generated_outline = llm_response.text

        if not generated_outline:
            logger.error("Execution halted: LLM returned an empty response.")
            return False

        # 3. Persist State
        logger.info("Persisting generated outline to database...")
        update_response = supabase.table("books").update({"outline": generated_outline}).eq("id", book_id).execute()
        
        if update_response.data:
            logger.info("Outline generation and persistence successful.")
            return True
            
        logger.error("Database update failed.")
        return False

    except Exception as e:
        logger.critical(f"System failure during outline generation: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target_id = sys.argv[1]
        generate_outline(target_id)
    else:
        logger.error("Usage: python -m src.generators.outline <book_id>")