"""
Booking.com Hotel Scraper - Contoh untuk pembelajaran
Mengambil rating dan jumlah ulasan dari halaman hotel
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ─────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────

HOTEL_URL = "https://www.booking.com/hotel/id/arena-villa.id.html"
OUTPUT_FILE = "data/hotel_data.json"

# Daftar proxy gratis (format: "ip:port")
# Ganti dengan proxy berbayar untuk hasil lebih stabil
PROXIES = [
    # Contoh format — isi dengan proxy kamu:
    # "123.45.67.89:8080",
    # "98.76.54.32:3128",
]

# User-Agent palsu agar tidak terdeteksi sebagai bot
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]


# ─────────────────────────────────────────
# FUNGSI ROTATING PROXY
# ─────────────────────────────────────────

def get_random_proxy():
    """Pilih proxy secara acak dari daftar."""
    if not PROXIES:
        return None  # Tanpa proxy jika daftar kosong
    proxy = random.choice(PROXIES)
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}


def get_random_headers():
    """Buat header HTTP palsu dengan User-Agent acak."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.booking.com/",
    }


# ─────────────────────────────────────────
# FUNGSI SCRAPING
# ─────────────────────────────────────────

def fetch_page(url, retries=3):
    """
    Ambil halaman web dengan retry otomatis.
    Setiap retry menggunakan proxy dan User-Agent berbeda.
    """
    for attempt in range(1, retries + 1):
        print(f"[Attempt {attempt}/{retries}] Mengambil halaman...")

        proxy = get_random_proxy()
        headers = get_random_headers()

        try:
            response = requests.get(
                url,
                headers=headers,
                proxies=proxy,
                timeout=15,
            )
            response.raise_for_status()
            print(f"✅ Berhasil! Status: {response.status_code}")
            return response.text

        except requests.RequestException as e:
            print(f"❌ Gagal: {e}")
            if attempt < retries:
                wait = random.uniform(3, 7)
                print(f"⏳ Menunggu {wait:.1f} detik sebelum retry...")
                time.sleep(wait)

    raise RuntimeError("Semua percobaan gagal. Coba lagi nanti.")


def parse_hotel_data(html):
    """
    Parse HTML dan ekstrak rating + jumlah ulasan.
    Booking.com sering mengubah struktur HTML-nya,
    jadi kita pakai beberapa selector sebagai fallback.
    """
    soup = BeautifulSoup(html, "html.parser")

    rating = None
    review_count = None

    # ── Cari Rating ──────────────────────────────────
    # Selector 1: atribut aria-label yang mengandung skor
    score_elem = soup.find("div", {"data-testid": "review-score-right-component"})
    if score_elem:
        score_text = score_elem.find("div", class_=lambda c: c and "ac4a7896c7" in c)
        if score_text:
            rating = score_text.get_text(strip=True)

    # Selector 2: fallback lewat aria-label
    if not rating:
        elem = soup.find(attrs={"aria-label": lambda v: v and "Skor" in v})
        if elem:
            rating = elem.get_text(strip=True)

    # ── Cari Jumlah Ulasan ───────────────────────────
    # Selector 1: data-testid
    review_elem = soup.find("div", {"data-testid": "review-score-right-component"})
    if review_elem:
        spans = review_elem.find_all("div")
        for span in spans:
            text = span.get_text(strip=True)
            if "ulasan" in text.lower() or "review" in text.lower():
                review_count = text
                break

    # Selector 2: fallback lewat teks
    if not review_count:
        for tag in soup.find_all(string=lambda t: t and "ulasan" in t.lower()):
            review_count = tag.strip()
            break

    return {
        "rating": rating or "Tidak ditemukan",
        "review_count": review_count or "Tidak ditemukan",
    }


# ─────────────────────────────────────────
# FUNGSI SIMPAN DATA
# ─────────────────────────────────────────

def load_existing_data(filepath):
    """Muat data lama dari file JSON jika ada."""
    path = Path(filepath)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"hotel_url": HOTEL_URL, "history": []}


def save_data(filepath, data):
    """Simpan data ke file JSON."""
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
    print("🏨 Booking.com Hotel Scraper")
    print("=" * 50)

    # 1. Ambil halaman
    html = fetch_page(HOTEL_URL)

    # 2. Parse data
    scraped = parse_hotel_data(html)
    print(f"\n📊 Hasil scraping:")
    print(f"   Rating       : {scraped['rating']}")
    print(f"   Jumlah Ulasan: {scraped['review_count']}")

    # 3. Tambahkan timestamp
    entry = {
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "rating": scraped["rating"],
        "review_count": scraped["review_count"],
    }

    # 4. Muat data lama lalu append
    all_data = load_existing_data(OUTPUT_FILE)
    all_data["history"].append(entry)
    all_data["last_updated"] = entry["scraped_at"]

    # 5. Simpan
    save_data(OUTPUT_FILE, all_data)
    print("\n✅ Selesai!")


if __name__ == "__main__":
    main()
