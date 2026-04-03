import sys
from playwright.sync_api import sync_playwright

# Ce script ne fait qu'une chose : prendre une URL et en faire un PDF


def capture(url, output_path):
    try:
        with sync_playwright() as p:
            # Lancement du navigateur
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Navigation avec timeout
            page.goto(url, wait_until="networkidle", timeout=60000)
            # Generation du PDF
            page.pdf(path=output_path)
            browser.close()
            print("Success")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Récupère les arguments envoyés par app.py
    if len(sys.argv) > 2:
        capture(sys.argv[1], sys.argv[2])