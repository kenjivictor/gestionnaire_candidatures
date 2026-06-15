import sys
import os
import tempfile
import cloudscraper
import pdfkit
from playwright.sync_api import sync_playwright
# Ce script ne fait qu'une chose : prendre une URL et en faire un PDF


def try_html_to_pdf(url, output_path):
    """
    Première tentative : télécharger le HTML et le convertir en PDF.
    Retourne True si succès, False sinon.
    """
    tmp_path = None
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=20)

        if response.status_code != 200:
            print(f"[HTML] HTTP {response.status_code}")
            return False

        html_content = response.text

        # Vérification : HTML vide ou trop court = site JS / SPA
        if len(html_content.strip()) < 500:
            print("[HTML] Contenu trop court, probablement une SPA.")
            return False

        # Sauvegarde dans un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            tmp.write(html_content.encode("utf-8"))
            tmp_path = tmp.name

        # Conversion HTML → PDF via wkhtmltopdf
        pdfkit.from_file(tmp_path, output_path)
        
        print("[HTML] Conversion PDF réussie.")
        return True

    except Exception as e:
        print(f"[HTML] Erreur : {e}")
        return False
    
    finally:
        # Suppression du fichier temporaire si créé
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                print("[HTML] Fichier temporaire supprimé.")
            except Exception as e:
                print(f"[HTML] Impossible de supprimer le fichier temporaire : {e}")



def try_playwright_pdf(url, output_path):
    """
    Deuxième tentative : Playwright (fallback).
    Retourne True si succès, False sinon.
    """
    try:
        with sync_playwright() as p:
            # --- User-Agent réaliste ---
            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
            
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()

            # Navigation
            page.goto(url, wait_until="networkidle", timeout=60000)

            # Gestion cookies
            cookie_selectors = [
                "button:has-text('Continuer sans accepter')",
                "button:has-text('Tout accepter')",
                "button:has-text('Accepter')",
                "#didomi-notice-agree-button",
                ".cookie-banner-accept"
            ]

            for selector in cookie_selectors:
                try:
                    if page.locator(selector).is_visible():
                        page.locator(selector).click()
                        page.wait_for_timeout(500)
                except:
                    pass

            # Génération PDF
            page.pdf(path=output_path)
            browser.close()

            print("[Playwright] PDF généré avec succès.")
            return True

    except Exception as e:
        print(f"[Playwright] Erreur : {e}")
        return False

def capture(url, output_path):
    """
    Fonction hybride :
    1) Essaye HTML → PDF
    2) Sinon fallback Playwright
    """
    print(f"--- Capture de {url} ---")

    # Tentative 1 : HTML → PDF
    if try_html_to_pdf(url, output_path):
        print("Success")
        return 0

    print("[Fallback] Passage à Playwright...")

    # Tentative 2 : Playwright
    if try_playwright_pdf(url, output_path):
        print("Success")
        return 0

    print("Error: Impossible de capturer la page.")
    return 1



if __name__ == "__main__":
    # Récupère les arguments envoyés par app.py
    if len(sys.argv) > 2:
        exit_code = capture(sys.argv[1], sys.argv[2])
        sys.exit(exit_code)