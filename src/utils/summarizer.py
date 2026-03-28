import os
import google.generativeai as genai
from src.database.connection import get_supabase_client

def get_n_minus_1_summary(book_id: str, current_ch_num: int):
    supabase = get_supabase_client()
    
    # Get all chapters from 1 to N-1
    res = supabase.table("chapters")\
        .select("content")\
        .eq("book_id", book_id)\
        .lt("chapter_number", current_ch_num)\
        .order("chapter_number")\
        .execute()
    
    if not res.data:
        return "This is the first chapter. No prior context."

    full_history = "\n\n".join([c['content'] for c in res.data])
    
    # Use Gemini for stylistic consistency in summaries
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Summarize the following chapters to provide context for the next one. Focus on plot points, character status, and established facts:\n\n{full_history}"
    
    response = model.generate_content(prompt)
    return response.text