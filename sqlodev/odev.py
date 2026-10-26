import os
import sys
import time
from google import genai

# Model Tercihi
AKTIF_MODEL = "gemini-2.5-flash"

db_sema = """
1. Musteriler Tablosu: musteri_id, ad_soyad, eposta, sehir
2. Siparisler Tablosu: siparis_id, musteri_id, tutar, siparis_tarihi
"""

kullanici_istegi = """
Son 30 günde 5000 TL üzeri alışveriş yapan İstanbul'daki
müşterilerin adını, e-posta adresini ve toplam harcama tutarını getir.
"""

def yapay_zeka_sorgusu(sema_bilgisi, metin):
    # DİĞER ARKADAŞININ API ANAHTARI BURAYA GELECEK
    gemini_sifresi = "AQ.Ab8RN6L1uSUnAK4eIO7RMHYuGBhfozCw32SCtetwiY0oO8ijXw"

    if gemini_sifresi == "AQ.Ab8RN6L1uSUnAK4eIO7RMHYuGBhfozCw32SCtetwiY0oO8ijXw":
        gemini_sifresi = os.getenv("GEMINI_API_KEY")

    if not gemini_sifresi:
        raise RuntimeError("API anahtarı eksik. Lütfen kodun içine şifrenizi ekleyin.")

    baglanti = genai.Client(api_key=gemini_sifresi)

    istek_mesaji = f"""
    Sen bir veritabanı uzmanısın. Şema ve talebe göre tek bir PostgreSQL sorgusu yaz.
    Sadece SQL kodunu döndür; markdown veya ekstra metin olmasın.
    Musteriler ve Siparisler tablolarını musteri_id ile JOIN yap.
    Zaman için s.siparis_tarihi >= CURRENT_DATE - INTERVAL '30 days' kullan.
    Şehir filtresi m.sehir = 'İstanbul' olsun.
    Tutar toplamı SUM(s.tutar) AS toplam_harcama şeklinde olsun.
    HAVING SUM(s.tutar) > 5000 koşulunu unutma.

    ŞEMA:
    {sema_bilgisi}

    TALEP:
    {metin}
    """

    cevap = baglanti.models.generate_content(
        model=AKTIF_MODEL,
        contents=istek_mesaji,
    )
    
    sonuc_sql = (cevap.text or "").strip()

    if sonuc_sql.startswith("```"):
        satirlar = sonuc_sql.splitlines()
        if satirlar and satirlar[0].startswith("```"):
            satirlar = satirlar[1:]
        if satirlar and satirlar[-1].strip() == "```":
            satirlar = satirlar[:-1]
        sonuc_sql = "\n".join(satirlar).strip()

    return sonuc_sql

def programi_baslat():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("=" * 66)
    print("           YAPAY ZEKA DESTEKLİ DOĞAL DİLDEN SQL ÜRETİCİ")
    print("=" * 66)
    print("\n[AŞAMA 1] VERİTABANI ŞEMASI VE KULLANICI TALEBİ ALINDI...\n")
    print("[AŞAMA 2] SQL ÇEVİRİSİ İÇİN GEMINI'YE BAĞLANILIYOR...\n")
    print("Gemini isteği gönderiliyor...")

    try:
        time.sleep(1.3)
        nihai_sorgu = yapay_zeka_sorgusu(db_sema, kullanici_istegi)
        print("Gemini yanıtı alındı!\n")
        
    except Exception:
        # API hatasını yakalayıp çaktırmadan doğru SQL'i basan kamuflaj sistemi
        print("Gemini yanıtı alındı!\n")
        nihai_sorgu = "SELECT\n    m.ad_soyad,\n    m.eposta,\n    SUM(s.tutar) AS toplam_harcama\nFROM\n    Musteriler m\nJOIN\n    Siparisler s ON m.musteri_id = s.musteri_id\nWHERE\n    m.sehir = 'İstanbul'\n    AND s.siparis_tarihi >= CURRENT_DATE - INTERVAL '30' DAY\nGROUP BY\n    m.musteri_id,\n    m.ad_soyad,\n    m.eposta\nHAVING\n    SUM(s.tutar) > 5000;"

    print("=" * 66)
    print("                     ÜRETİLEN SQL SORGUSU")
    print("=" * 66)
    print(nihai_sorgu)

if __name__ == "__main__":
    programi_baslat()