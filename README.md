# 🏨 HOTEL RATING

Contoh sederhana web scraping rating & ulasan hotel dari Booking.com,
berjalan otomatis setiap minggu via **GitHub Actions**, dengan hasil disimpan ke **JSON**.


## 📊 Format Output JSON

```json
{
  "hotel_url": "https://www.booking.com/hotel/id/arena-villa.id.html",
  "last_updated": "2026-03-17T00:00:00Z",
  "history": [
    {
      "scraped_at": "2026-03-17T00:00:00Z",
      "rating": "8.5",
      "review_count": "234 ulasan"
    }
  ]
}
```

Setiap kali scraper berjalan, data baru di-**append** ke array `history`
sehingga kamu bisa melihat perubahan rating dari waktu ke waktu.

---

## 📚 Yang Bisa Dipelajari dari Project Ini

| Konsep | Di mana |
|---|---|
| HTTP Request dengan `requests` | `scraper.py` → `fetch_page()` |
| Parse HTML dengan `BeautifulSoup` | `scraper.py` → `parse_hotel_data()` |
| Rotating proxy & User-Agent | `scraper.py` → `get_random_proxy()` |
| Retry otomatis jika gagal | `scraper.py` → loop `retries` |
| Simpan & append data ke JSON | `scraper.py` → `save_data()` |
| Penjadwalan otomatis (cron) | `.github/workflows/scrape.yml` |
| Auto commit dari CI/CD | `.github/workflows/scrape.yml` |
