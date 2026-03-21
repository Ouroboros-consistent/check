"""
Booking.com Hotel Scraper - Selenium + Chrome Headless
Pakai browser sungguhan → jauh lebih susah diblokir
100% gratis, tidak butuh layanan eksternal
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ─────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────

HOTEL_URL   = "https://www.booking.com/hotel/id/arena-villa.id.html"
OUTPUT_FILE = "data/hotel_data.json"


# ─────────────────────────────────────────
# SETUP CHROME
# ─────────────────────────────────────────

def create_driver():
    """Buat Chrome headless yang susah dideteksi sebagai bot."""
    options = Options()

    # Mode headless — tidak perlu monitor (wajib di server)
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Sembunyikan tanda-tanda bot
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # User-Agent manusia
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )

    # Bahasa Indonesia
    options.add_argument("--lang=id-ID")
    options.add_experimental_option("prefs", {"intl.accept_languages": "id,id_ID"})

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Hapus property webdriver agar tidak terdeteksi
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


# ─────────────────────────────────────────
# SCRAPING
# ─────────────────────────────────────────

def scrape_hotel(url):
    """Buka halaman hotel dan ambil rating + jumlah ulasan."""
    driver = create_driver()

    try:
        print(f"🌐 Membuka: {url}")
        driver.get(url)

        # Tunggu halaman dimuat (maks 15 detik)
        wait = WebDriverWait(driver, 15)

        # Jeda acak seperti manusia membaca halaman
        time.sleep(random.uniform(2, 4))

        # Scroll sedikit ke bawah (meniru perilaku manusia)
        driver.execute_script("window.scrollBy(0, 400)")
        time.sleep(random.uniform(1, 2))

        print(f"📄 Judul halaman: {driver.title}")
        print(f"📏 Ukuran halaman: {len(driver.page_source):,} karakter")

        rating       = None
        review_count = None

        # ── Cari Rating ──────────────────────────────────────────
        # Selector 1: data-testid
        selectors_rating = [
            "[data-testid='review-score-component'] [class*='score']",
            "[data-testid='review-score-right-component'] div:first-child",
            ".bui-review-score__badge",
            "[class*='review-score-badge']",
            "[aria-label*='Skor']",
            "[aria-label*='score']",
        ]
        for sel in selectors_rating:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                text = elem.text.strip()
                if text and any(c.isdigit() for c in text):
                    rating = text
                    print(f"  ✅ Rating via '{sel}': {rating}")
                    break
            except Exception:
                continue

        # ── Cari Jumlah Ulasan ───────────────────────────────────
        selectors_review = [
            "[data-testid='review-score-right-component'] div:nth-child(2)",
            "[data-testid='review-score-right-component'] div:nth-child(3)",
            ".bui-review-score__text",
            "[class*='review-score__text']",
        ]
        for sel in selectors_review:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                text = elem.text.strip()
                if text and ("ulasan" in text.lower() or "review" in text.lower() or text.isdigit()):
                    review_count = text
                    print(f"  ✅ Ulasan via '{sel}': {review_count}")
                    break
            except Exception:
                continue

        # ── Fallback: cari lewat teks halaman ───────────────────
        if not rating or not review_count:
            import re
            page_text = driver.find_element(By.TAG_NAME, "body").text

            if not rating:
                m = re.search(r'\b([7-9]\.\d|10\.0)\b', page_text)
                if m:
                    rating = m.group(1)
                    print(f"  ✅ Rating via teks: {rating}")

            if not review_count:
                m = re.search(r'(\d[\d.,]+)\s*(ulasan|review)', page_text, re.I)
                if m:
                    review_count = f"{m.group(1)} {m.group(2)}"
                    print(f"  ✅ Ulasan via teks: {review_count}")

        return {
            "rating": rating or "Tidak ditemukan",
            "review_count": review_count or "Tidak ditemukan",
        }

    finally:
        driver.quit()


# ─────────────────────────────────────────
# SIMPAN DATA
# ─────────────────────────────────────────

def load_existing_data(filepath):
    path = Path(filepath)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"hotel_url": HOTEL_URL, "history": []}


def save_data(filepath, data):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Data disimpan ke {filepath}")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("=" * 50)
    print("🏨 Booking.com Scraper — Selenium")
    print("=" * 50)

    scraped = scrape_hotel(HOTEL_URL)

    print(f"\n📊 Hasil scraping:")
    print(f"   Rating       : {scraped['rating']}")
    print(f"   Jumlah Ulasan: {scraped['review_count']}")

    entry = {
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "rating": scraped["rating"],
        "review_count": scraped["review_count"],
    }

    all_data = load_existing_data(OUTPUT_FILE)
    all_data["history"].append(entry)
    all_data["last_updated"] = entry["scraped_at"]
    save_data(OUTPUT_FILE, all_data)
    print("\n✅ Selesai!")


if __name__ == "__main__":
    main()
