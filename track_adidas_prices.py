import gspread
from google.oauth2.service_account import Credentials
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- Google Sheets Setup ---
SHEET_ID = 'YOUR_SHEET_ID'
TRACKING_TAB = 'Tracking List'
HISTORY_TAB = 'Price History'

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
gc = gspread.authorize(CREDS)
sh = gc.open_by_key(SHEET_ID)
tracking_ws = sh.worksheet(TRACKING_TAB)
history_ws = sh.worksheet(HISTORY_TAB)

def get_adidas_price(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Try typical selectors; adjust if needed
    title = soup.find('h1')
    price = soup.find('div', class_='gl-price-item')
    sale = soup.find('div', class_='gl-price-item--sale')
    product_title = title.get_text(strip=True) if title else ""
    product_price = price.get_text(strip=True).replace('$','') if price else ""
    sale_tag = "Sale" if sale else ""
    return product_title, product_price, sale_tag

def main():
    products = tracking_ws.get_all_records()
    today = datetime.today().strftime('%Y-%m-%d')
    for product in products:
        url = product['Product URL']
        name = product.get('Product Name', '')
        try:
            title, price, sale = get_adidas_price(url)
        except Exception as e:
            title, price, sale = "", "", ""
        row = [today, url, title or name, price, sale]
        history_ws.append_row(row, value_input_option="USER_ENTERED")

if __name__ == "__main__":
    main()
