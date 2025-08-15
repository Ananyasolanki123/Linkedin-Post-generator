import json
from collections import Counter
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

SHEET_NAME = "Linkedin Post Generator(Responses)"  # Your sheet name

def _get_gspread_client():
    try:
        # Use the dict directly from secrets
        sa_info = st.secrets["gcp_service_account"]
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Sheets authentication failed: {e}")
        raise


def fetch_latest_form_data():
    client = _get_gspread_client()
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
