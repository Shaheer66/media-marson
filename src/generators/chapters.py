import re
import logging
from typing import List, Dict, Any
from src.database.connection import get_supabase_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_and_initialize_chapters(book_id: str) -> bool:
    """
    Parses the raw outline text from the books table and initializes 
    individual rows in the chapters table.
    """
    try:
        supabase = get_supabase_client()

        # 1. Fetch the raw outline
        response = supabase.table("books").select("outline").eq("id", book_id).single().execute()
        if not response.data or not response.data.get("outline"):
            logger.error("No outline found to parse.")
            return False

        raw_outline = response.data["outline"]

        #  Parse chapters using Regex
        # Pattern looks for "Chapter X: Title" followed by the description block
        chapters_data: List[Dict[str, Any]] = []
        
        # This regex identifies "Chapter" followed by a number/title and captures 
        # the subsequent text until the next "Chapter" or end of string.
        segments = re.findall(r"(?:Chapter\s+\d+:?\s*)(.*?)(?=\n(?:Chapter\s+\d+:?)|$)", raw_outline, re.DOTALL)

        for index, content in enumerate(segments, start=1):
            lines = content.strip().split('\n')
            title = lines[0].strip()
            summary = " ".join(lines[1:]).strip()

            chapters_data.append({
                "book_id": book_id,
                "chapter_number": index,
                "title": title,
                "summary": summary,
                "status": "pending_generation"
            })

        if not chapters_data:
            logger.error("Failed to parse any chapters from the outline.")
            return False

        #  Bulk Insert to Chapters Table
        logger.info(f"Inserting {len(chapters_data)} chapters for Book ID: {book_id}")
        insert_response = supabase.table("chapters").insert(chapters_data).execute()

        if insert_response.data:
            # Update Book Status
            supabase.table("books").update({"status": "outline_generated"}).eq("id", book_id).execute()
            logger.info("Chapters initialized and book status updated.")
            return True

        return False

    except Exception as e:
        logger.critical(f"Chapter initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        parse_and_initialize_chapters(sys.argv[1])
    else:
        logger.error("Usage: python -m src.generators.chapters <book_id>")