import logging
import sys
from src.generators.content import generate_chapter_content

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_full_generation(book_id: str):
    """
    Orchestrates the sequential generation of all chapters for a given book.
    """
    logger.info(f"Starting full content generation for Book ID: {book_id}")
    
    chapters_completed = 0
    
    while True:
        
        success = generate_chapter_content(book_id)
        
        if not success:
            break
            
        chapters_completed += 1
        logger.info(f"Progress update: {chapters_completed} chapters processed so far.")

    logger.info("Generation loop finished. Check your database for final content.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_book_id = sys.argv[1]
        run_full_generation(target_book_id)
    else:
        logger.error("Usage: python main.py <book_id>")