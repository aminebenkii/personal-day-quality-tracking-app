import gspread
from oauth2client.service_account import ServiceAccountCredentials
from app.config import SHEET_ID, WORKSHEET_NAME
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CREDENTIALS_FILE = ROOT_DIR / "app" / "creds.json"  # Update if your JSON key has a different filename

def test_google_sheets():
    # Define scope
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Authenticate
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    # Open the sheet
    sheet = client.open_by_key(SHEET_ID)
    try:
        worksheet = sheet.worksheet(WORKSHEET_NAME)
    except:
        worksheet = sheet.add_worksheet(title=WORKSHEET_NAME, rows="1000", cols="20")

    # Dummy test data
    data = {
        "date": ["2025-08-31"],
        "sleep": [4],
        "energy": [5],
        "gratitude": ["Testing Google Sheets ✅"],
        "notes": ["Connection successful!"]
    }

    df = pd.DataFrame(data)

    # If the sheet is empty, add headers
    if not worksheet.get_all_values():
        worksheet.append_row(list(df.columns))

    # Convert all values to strings before appending
    row = [str(x) for x in list(df.iloc[0])]
    worksheet.append_row(row)

    print("✅ Success! Row added to Google Sheets.")
    
if __name__ == "__main__":
    test_google_sheets()
