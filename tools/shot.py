import sys
from playwright.sync_api import sync_playwright
import time
# Ce script ne fait qu'une chose : prendre une URL et en faire un PDF


def capture(url, output_path):
    try:
        with sync_playwright() as p:
            # Lancement du navigateur
            # browser = p.chromium.launch(headless=True)
            browser = p.chromium.launch()
            page = browser.new_page()
            # Navigation avec timeout
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # --- Gestion des cookies 
            # On définit une liste de sélecteurs courants pour les boutons de cookies
            cookie_selectors = [
                "button:has-text('Continuer sans accepter')",
                "button:has-text('Tout accepter')", 
                "button:has-text('Accepter')",
                "#didomi-notice-agree-button",
                ".cookie-banner-accept"
            ]

            for selector in cookie_selectors:
                try:
                    # On vérifie si le bouton est visible et on clique
                    if page.locator(selector).is_visible():
                        page.locator(selector).click()
                        page.wait_for_timeout(500) # Petit délai pour que la popup disparaisse
                except:
                    continue
            
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