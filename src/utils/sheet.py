import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
from src.database.connection import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_sheets_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
    return gspread.authorize(creds)

def sync_supabase_to_sheets(book_id: str, sheet_name: str):
    """
    Updates the Google Sheet dashboard with the latest status from Supabase.
    """
    try:
        supabase = get_supabase_client()
        client = get_sheets_client()
        sheet = client.open(sheet_name).sheet1

        res = supabase.table("books").select("title, status, outline").eq("id", book_id).single().execute()
        book = res.data

        # Find the row in the sheet by Book ID (assuming ID is in Column A)
        cell = sheet.find(book_id)
        row = cell.row

        # Update Status (Col B) and Title (Col C)
        sheet.update_cell(row, 2, book['status'])
        sheet.update_cell(row, 3, book['title'])
        
        logger.info(f"Successfully synced {book['title']} to Google Sheets.")
        return True

    except Exception as e:
        logger.error(f"Sheets Sync Error: {e}")
        return False

def fetch_new_tasks(sheet_name: str):
    """
    Looks for rows in the sheet marked as 'Pending' to start new Supabase records.
    """
    client = get_sheets_client()
    sheet = client.open(sheet_name).sheet1
    records = sheet.get_all_records()
    
    new_tasks = [r for r in records if r.get('Status') == 'Pending']
    return new_tasks