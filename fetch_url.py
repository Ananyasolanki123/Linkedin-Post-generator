import gspread
from google.oauth2.service_account import Credentials
from collections import Counter

SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Authenticate
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

SHEET_NAME = "Linkedin Post Generator(Responses)"  # Your sheet name

def fetch_latest_form_data():
    """
    Fetch and clean the latest Google Form responses from the sheet.
    Handles duplicate column names by appending _2, _3, etc.
    Returns a list of dictionaries (one dict per row).
    """
    sheet = client.open(SHEET_NAME).sheet1
    data = sheet.get_all_values()

    if not data:
        return []

    # First row is header
    headers = data[0]

    # Remove extra spaces & make unique
    clean_headers = []
    counts = Counter()
    for h in headers:
        h = h.strip()
        counts[h] += 1
        if counts[h] > 1:
            h = f"{h}_{counts[h]}"
        clean_headers.append(h)

    # Create list of dicts with clean headers
    rows = [dict(zip(clean_headers, row)) for row in data[1:]]
    return rows

# Quick test
if __name__ == "__main__":
    from pprint import pprint
    pprint(fetch_latest_form_data())
