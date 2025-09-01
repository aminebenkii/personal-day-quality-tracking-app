import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_ID, WORKSHEET_NAME
import pandas as pd
from pathlib import Path   
from gspread_formatting import CellFormat, textFormat, format_cell_range
from metrics import metrics  
import os
import json


# ROOT_DIR = Path(__file__).resolve().parents[1]
# CREDENTIALS_FILE = ROOT_DIR / "app" / "creds.json"  

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)


def create_evaluation_grid_if_needed(client):
    spreadsheet = client.open_by_key(SHEET_ID)
    try:
        sheet = spreadsheet.worksheet("EvaluationGrid")
    except:
        sheet = spreadsheet.add_worksheet(title="EvaluationGrid", rows="1000", cols="3")

        # Create grid rows
        rows = []
        for key, data in metrics.items():
            label = data["label"]
            for score in range(1, 6):
                meaning = data["legend"][score]
                rows.append([label, str(score), meaning])

        # Insert headers + data
        headers = ["Metric", "Rating", "Meaning"]
        sheet.append_row(headers)
        for row in rows:
            sheet.append_row(row)

        # Format header
        header_format = CellFormat(
            textFormat=textFormat(bold=True),
            horizontalAlignment="CENTER"
        )
        format_cell_range(sheet, "A1:C1", header_format)


def save_to_google_sheets(data_dict: dict):
    """
    Saves a single day's reflection data to Google Sheets.
    Automatically creates headers if the sheet is empty.
    """

    # Define Google API scope
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Authenticate with Google
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    create_evaluation_grid_if_needed(client)

    # Open sheet & worksheet
    sheet = client.open_by_key(SHEET_ID)
    try:
        worksheet = sheet.worksheet(WORKSHEET_NAME)
    except:
        worksheet = sheet.add_worksheet(title=WORKSHEET_NAME, rows="1000", cols="20")

    # Convert dict to DataFrame
    df = pd.DataFrame([data_dict])

    existing_data = worksheet.get_all_values()

    if not existing_data or existing_data[0] != list(df.columns):
        worksheet.clear()
        worksheet.append_row(list(df.columns))


    # Convert all values to strings before appending (avoid int64 JSON errors)
    worksheet.append_row([str(x) for x in df.iloc[0]])
