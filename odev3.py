import json
import os
from google import genai
from google.genai import errors

# ================= AYARLAR =================
# Senin API anahtarın
API_ANAHTARI = "API_ANAHTARIM_GIZLENMISTIR"
DOSYA_ADI = "urunler.json"
# ===========================================

def verileri_yukle():
    """urunler.json dosyasından kayıtları okur, dosya bozuk veya yoksa boş liste döner."""
    if not os.path.exists(DOSYA_ADI):
        return []
    try:
        with open(DOSYA_ADI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def verileri_kaydet(veriler):
    """Verileri JSON formatında dosyaya kaydeder."""
    with open(DOSYA_ADI, 'w', encoding='utf-8') as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)

def yeni_urun_kodu_uret(veriler):
    """Mevcut URN-XXXX kodlarını analiz ederek bir sonraki benzersiz ürün kodunu üretir."""
    if not veriler:
        return "URN-0001"
    max_num = 0
    for urun in veriler:
        kod = urun.get("urun_kodu", "")
        if kod.startswith("URN-"):
            try:
                num = int(kod.split("-")[1])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"URN-{max_num + 1:04d}"

def e_ticaret_api_simulasyonu(urun_talebi):
    """Senin bulduğun yeni Interactions API yapısını kullanarak Gemini'den JSON verisi çeker."""
    client = genai.Client(api_key=API_ANAHTARI)

    sistem_mesaji = """
    Sen kurumsal bir e-ticaret sisteminin arka planında çalışan bir veri yapılandırma asistanısın.
    Kullanıcının girdiği ham ürün bilgilerini analiz edip, veritabanına kaydedilebilmesi için SADECE JSON formatında yanıt vermelisin.

    JSON nesnesi kesinlikle şu anahtarları içermelidir:
    {
        "urun_adi": "Kısa ve optimize edilmiş ürün adı",
        "kategori": "Uygun e-ticaret kategorisi",
        "seo_etiketleri": "3 adet virgülle ayrılmış SEO etiketi",
        "satis_aciklamasi": "Müşteriyi ikna edecek profesyonel 2 cümle"
    }
    JSON dışında hiçbir açıklama yazma.
    """

    try:
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=f"{sistem_mesaji}\nKullanıcının ürün talebi:\n{urun_talebi}"
        )
        
        yapilandirilmis_veri = interaction.output_text.strip()
        
        # Eğer model ```json ... ``` etiketleri eklerse onları temizliyoruz
        if yapilandirilmis_veri.startswith("```json"):
            yapilandirilmis_veri = yapilandirilmis_veri[7:]
        if yapilandirilmis_veri.endswith("```"):
            yapilandirilmis_veri = yapilandirilmis_veri[:-3]
            
        return json.loads(yapilandirilmis_veri.strip())

    except errors.APIError as e:
        print(f"\n[API HATASI] Açıklama: {e}")
        return None
    except Exception as e:
        print(f"\n[SİSTEM HATASI] Beklenmeyen bir istisna oluştu: {e}")
        return None

def stok_durum_uyarisi(stok):
    """Stok miktarına göre ödevde istenen uyarı mesajlarını yazdırır."""
    if stok == 0:
        print("[UYARI] STOKTA YOK")
    elif 1 <= stok <= 4:
        print(f"[UYARI] KRİTİK STOK! Yalnızca {stok} adet kaldı.")

def yeni_urun_ekle(veriler):
    """Kullanıcıdan verileri alır, senin API fonksiyonunu çağırır ve kaydeder."""
    aciklama = input("Ürün açıklaması: ").strip()
    
    # Negatif fiyat kontrolü
    while True:
        try:
            fiyat = float(input("Ürün fiyatı: "))
            if fiyat < 0:
                print("Fiyat negatif olamaz. Lütfen tekrar deneyin.")
                continue
            break
        except ValueError:
            print("Lütfen geçerli bir sayı girin.")
            
    # Negatif stok kontrolü
    while True:
        try:
            stok = int(input("Stok miktarı: "))
            if stok < 0:
                print("Stok negatif olamaz. Lütfen tekrar deneyin.")
                continue
            break
        except ValueError:
            print("Lütfen geçerli bir tam sayı girin.")
            
    print("\n[API] Ürün bilgileri oluşturuluyor...")
    api_verisi = e_ticaret_api_simulasyonu(aciklama)
    
    if not api_verisi:
        print("[HATA] API'den geçerli bir veri alınamadığı için kayıt iptal edildi.")
        return
        
    # Zorunlu alanların kontrolü
    gerekli_alanlar = ["urun_adi", "kategori", "seo_etiketleri", "satis_aciklamasi"]
    if not all(alan in api_verisi for alan in gerekli_alanlar):
        print("[HATA] API'den eksik veri geldiği için kayıt iptal edildi.")
        return
        
    urun_kodu = yeni_urun_kodu_uret(veriler)
    yeni_urun = {
        "urun_kodu": urun_kodu,
        "urun_adi": api_verisi["urun_adi"],
        "kategori": api_verisi["kategori"],
        "seo_etiketleri": api_verisi["seo_etiketleri"],
        "satis_aciklamasi": api_verisi["satis_aciklamasi"],
        "fiyat": fiyat,
        "stok": stok
    }
    
    veriler.append(yeni_urun)
    verileri_kaydet(veriler)
    
    print("\n[BAŞARILI] Ürün kaydedildi.")
    print(f"Ürün Kodu: {urun_kodu}")
    print(f"Ürün Adı: {yeni_urun['urun_adi']}")
    print(f"Kategori: {yeni_urun['kategori']}")
    print(f"Fiyat: {fiyat} TL")
    print(f"Stok: {stok}")
    print(f"SEO: {yeni_urun['seo_etiketleri']}")
    stok_durum_uyarisi(stok)

def urunleri_listele(veriler):
    """Kayıtlı tüm ürünleri ödevde istenen formatta listeler."""
    if not veriler:
        print("\n[UYARI] Listelenecek ürün bulunamadı.")
        return
    print("\n--- KAYITLI ÜRÜNLER ---")
    for u in veriler:
        print("-" * 50)
        print(f"Kod: {u['urun_kodu']} | Ad: {u['urun_adi']} | Kategori: {u['kategori']} | Fiyat: {u['fiyat']} TL | Stok: {u['stok']}")
        stok_durum_uyarisi(u['stok'])
    print("-" * 50)

def urun_ara(veriler):
    """Ürün kodu veya adında kısmi eşleşmeli ve büyük/küçük harf duyarsız arama yapar."""
    kelime = input("Aranacak ürün (isim veya kod): ").strip().lower()
    bulunanlar = [u for u in veriler if kelime in u['urun_adi'].lower() or kelime in u['urun_kodu'].lower()]
    
    if bulunanlar:
        print(f"\n[SONUÇ] {len(bulunanlar)} ürün bulundu:")
        for u in bulunanlar:
            print(f"- {u['urun_kodu']} : {u['urun_adi']}")
    else:
        print("\nÜrün bulunamadı.")

def stok_guncelle(veriler):
    """Girilen ürün koduna göre stok miktarını günceller."""
    kod = input("Stok güncellenecek ürün kodu (Örn: URN-0001): ").strip().upper()
    urun = next((u for u in veriler if u['urun_kodu'].upper() == kod), None)
    
    if not urun:
        print("\nBelirtilen kodla ürün bulunamadı.")
        return
        
    while True:
        try:
            yeni_stok = int(input(f"{urun['urun_adi']} için yeni stok miktarı: "))
            if yeni_stok < 0:
                print("Stok negatif olamaz. Lütfen tekrar deneyin.")
                continue
            break
        except ValueError:
            print("Lütfen sayısal bir tam sayı değeri girin.")
            
    eski_stok = urun['stok']
    urun['stok'] = yeni_stok
    verileri_kaydet(veriler)
    print(f"\n[BAŞARILI] Stok {eski_stok} -> {yeni_stok} olarak güncellendi.")
    stok_durum_uyarisi(yeni_stok)

def ana_menu():
    """Sistemi çalıştıran ana menü döngüsü."""
    veriler = verileri_yukle()
    
    while True:
        print("\n" + "=" * 30)
        print(" E-TİCARET YÖNETİM PANELİ ")
        print("=" * 30)
        print("1- Yeni Ürün Ekle")
        print("2- Ürünleri Listele")
        print("3- Ürün Ara")
        print("4- Stok Güncelle")
        print("5- Çıkış")
        
        secim = input("\nSeçiminiz: ").strip()
        
        if secim == "1":
            yeni_urun_ekle(veriler)
        elif secim == "2":
            urunleri_listele(veriler)
        elif secim == "3":
            urun_ara(veriler)
        elif secim == "4":
            stok_guncelle(veriler)
        elif secim == "5":
            print("\nÇıkış yapılıyor. İyi çalışmalar!")
            break
        else:
            print("\nHatalı seçim! Lütfen 1-5 arasında bir rakam giriniz.")

if __name__ == "__main__":
    ana_menu()