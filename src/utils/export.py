import os
import logging
from datetime import datetime
from src.database.connection import get_supabase_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def export_book_to_markdown(book_id: str) -> str:
    """
    Compiles all completed chapters into a single Markdown file.
    """
    try:
        supabase = get_supabase_client()
 
        book_res = supabase.table("books").select("title, outline").eq("id", book_id).single().execute()
        if not book_res.data:
            logger.error("Book record not found.")
            return ""
        
        title = book_res.data['title']
      
        chapters_res = supabase.table("chapters")\
            .select("chapter_number, title, content")\
            .eq("book_id", book_id)\
            .eq("status", "completed")\
            .order("chapter_number")\
            .execute()

        chapters = chapters_res.data
        if not chapters:
            logger.warning("No completed chapters found for export.")
            return ""

         
        content_blocks = [f"# {title}\n", "---", "## Table of Contents"]
        
   
        for ch in chapters:
            content_blocks.append(f"- Chapter {ch['chapter_number']}: {ch['title']}")
        
        content_blocks.append("---\n")

    
        for ch in chapters:
            content_blocks.append(f"## Chapter {ch['chapter_number']}: {ch['title']}")
            content_blocks.append(ch['content'])
            content_blocks.append("\n---\n")

        full_markdown = "\n".join(content_blocks)

        # 4. Save to Disk
        os.makedirs("exports", exist_ok=True)
        filename = f"exports/{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_markdown)

        logger.info(f" Book exported successfully: {filename}")
        return filename

    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        return ""

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        export_book_to_markdown(sys.argv[1])