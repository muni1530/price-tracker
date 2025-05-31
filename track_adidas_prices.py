import gspread
from google.auth import default
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# --- Google Sheets Setup ---
SHEET_ID = os.environ.get('SHEET_ID')
TRACKING_TAB = 'Tracking List'
HISTORY_TAB = 'Price History'

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS, _ = default(scopes=SCOPES)
gc = gspread.authorize(CREDS)
sh = gc.open_by_key(SHEET_ID)
tracking_ws = sh.worksheet(TRACKING_TAB)
history_ws = sh.worksheet(HISTORY_TAB)

def get_adidas_price(url):
    print(f"Fetching: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.get(url, headers=headers, timeout=10)
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
    print(f"Found {len(products)} products to track.")
    today = datetime.today().strftime('%Y-%m-%d')
    for product in products:
        url = product['Product URL']
        name = product.get('Product Name', '')
        try:
            title, price, sale = get_adidas_price(url)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            title, price, sale = "", "", ""
        row = [today, url, title or name, price, sale]
        history_ws.append_row(row, value_input_option="USER_ENTERED")
        print(f"Logged: {title or name} | Price: {price} | Sale: {sale}")
    print("✅ All products processed and logged!")

if __name__ == "__main__":
    main()
