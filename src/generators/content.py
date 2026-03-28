import logging
from typing import List, Optional
from src.database.connection import get_supabase_client, get_gemini_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CHAPTER_PROMPT_TEMPLATE = """
You are an expert author writing a book titled: "{title}".
Below is the full outline for context:
{outline}

Previous Chapter Summaries (for continuity):
{history}

Current Task: Write the full content for Chapter {number}: {chapter_title}.
Chapter Summary to expand: {summary}

Requirements:
- Write in a professional, engaging tone.
- Minimum 1000 words.
- Use markdown formatting for subheadings.
- Do not include introductory filler like "Here is the chapter."
"""

def generate_chapter_content(book_id: str) -> bool:
    try:
        supabase = get_supabase_client()
        
        # 1. Fetch Global Book Data
        book_res = supabase.table("books").select("title, outline").eq("id", book_id).single().execute()
        book_data = book_res.data

        # 2. Fetch the Next Pending Chapter
        chapter_res = supabase.table("chapters").select("*").eq("book_id", book_id).eq("status", "pending_generation").order("chapter_number").limit(1).execute()
        
        if not chapter_res.data:
            logger.info("No pending chapters found. Book generation complete.")
            return False
            
        current_chapter = chapter_res.data[0]
        chapter_id = current_chapter['id']

        # 3. Fetch History (Previous Chapters)
        history_res = supabase.table("chapters").select("summary").eq("book_id", book_id).lt("chapter_number", current_chapter['chapter_number']).order("chapter_number").execute()
        history_text = "\n".join([f"- {c['summary']}" for c in history_res.data]) if history_res.data else "First Chapter."

        # 4. LLM Generation
        model = get_gemini_model()
        prompt = CHAPTER_PROMPT_TEMPLATE.format(
            title=book_data['title'],
            outline=book_data['outline'],
            history=history_text,
            number=current_chapter['chapter_number'],
            chapter_title=current_chapter['title'],
            summary=current_chapter['summary']
        )

        logger.info(f"Generating Chapter {current_chapter['chapter_number']}...")
        response = model.generate_content(prompt)
        content = response.text

        # 5. Save and Update Status
        supabase.table("chapters").update({
            "content": content,
            "status": "completed"
        }).eq("id", chapter_id).execute()

        logger.info(f"Chapter {current_chapter['chapter_number']} saved successfully.")
        return True

    except Exception as e:
        logger.critical(f"Content generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        generate_chapter_content(sys.argv[1])