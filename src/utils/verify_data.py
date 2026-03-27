from src.database.connection import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_book_data(book_id: str):
    supabase = get_supabase_client()
    
    
    response = supabase.table("books").select("title, pre_outline_notes, status").eq("id", book_id).single().execute()
    
    if not response.data:
        logger.error(f"No book found with ID: {book_id}")
        return
    
    book = response.data
    logger.info(f"--- Data Verification for Book ID: {book_id} ---")
    logger.info(f"Title: {book.get('title')}")
    logger.info(f"Status: {book.get('status')}")
    
    notes = book.get('pre_outline_notes', '')
    if len(notes) < 50:
        logger.warning(" Notes are very short. The AI might produce a generic outline.")
    else:
        logger.info(" Notes look sufficient for generation.")

if __name__ == "__main__":
    # Use the ID from your previous successful run
    TARGET_ID = "720348fd-2d45-40a3-b909-807efa67429a"
    verify_book_data(TARGET_ID)