import time
import csv
import random

# Başlangıç Kodu (Yavaş olan O(N^2) versiyon)
def bul(l):
    r = []
    for i in range(len(l)):
        for j in range(i + 1, len(l)):
            if l[i] == l[j] and l[i] not in r:
                r.append(l[i])
    return r

# TODO 1: Gemini yardımıyla optimize edilmiş kod (Hızlı O(N) versiyon)
# TODO 1: Gemini yardımıyla optimize edilmiş kod (Hızlı O(N) versiyon)
def bul_optimize(l: list) -> list:
    # 1. Adım: Hangi elemanların tekrar ettiğini bul
    gorulenler = set()
    tekrar_edenler = set()
    
    for eleman in l:
        if eleman in gorulenler:
            tekrar_edenler.add(eleman)
        else:
            gorulenler.add(eleman)
            
    # 2. Adım: İlk görülme sırasını koruyarak sonuç listesine ekle
    r = []
    eklenenler = set()
    for eleman in l:
        if eleman in tekrar_edenler and eleman not in eklenenler:
            r.append(eleman)
            eklenenler.add(eleman)
            
    return r

# Doğruluk testleri (PDF'teki test senaryoları)
def dogruluk_testleri():
    assert bul_optimize([]) == []
    assert bul_optimize([7]) == []
    assert bul_optimize([1, 2, 3]) == []
    assert bul_optimize([3, 1, 3, 2, 1]) == [3, 1]
    assert bul_optimize([4, 2, 2, 4, 3, 3]) == [4, 2, 3]
    print("Doğruluk testleri: BAŞARILI (Tüm testler geçildi)")

# Veri setini yükleme (Videodaki hocanın istediği 5000 kitaplık veri seti)
veriler = []
try:
    with open("5000_kitap_veriseti.csv", mode="r", encoding="utf-8") as dosya:
        okuyucu = csv.reader(dosya)
        for satir in okuyucu:
            if satir:
                # Kitap isimlerini veya tüm satırı string olarak listeye ekliyoruz
                veriler.append(satir[0]) 
except FileNotFoundError:
    print("UYARI: '5000_kitap_veriseti.csv' bulunamadı. Rastgele veri üretiliyor...")
    random.seed(42)
    veriler = [random.randint(1, 1000) for _ in range(5000)]

# Veri kümesini 5000 ile sınırlayalım (Ne olur ne olmaz)
veriler = veriler[:5000]

print(f"\nİşlenen veri sayısı: {len(veriler)}")

# Eski kodun performans ölçümü
baslangic = time.perf_counter()
sonuc_eski = bul(veriler)
eski_sure = time.perf_counter() - baslangic
print(f"Eski fonksiyon çalışma süresi: {eski_sure:.6f} saniye")

# TODO 2: Optimize kodun performans ölçümü
baslangic = time.perf_counter()
sonuc_yeni = bul_optimize(veriler)
yeni_sure = time.perf_counter() - baslangic
print(f"Optimize fonksiyon çalışma süresi: {yeni_sure:.6f} saniye")

# TODO 3: Sonuçların aynı olduğunu kontrol etme
assert sonuc_eski == sonuc_yeni, "HATA: İki fonksiyonun ürettiği sonuçlar birbirinden farklı!"
print("Sonuç eşleşme kontrolü: BAŞARILI (Eski ve yeni kod aynı sonucu üretiyor)")

# TODO 4: Hızlanma katsayısını hesaplama
# Sıfıra bölme hatasını engellemek için küçük bir tolerans payı ekliyoruz
hizlanma = eski_sure / (yeni_sure if yeni_sure > 0 else 0.000001)
print(f"Hızlanma Oranı: {hizlanma:.2f} kat")

# Doğruluk testlerini çalıştır
dogruluk_testleri()

# TODO 5: Raporu .txt dosyasına yazdırma
rapor_metni = f"""KOD PERFORMANS RAPORU
Veri sayisi: {len(veriler)}
Eski kod suresi: {eski_sure:.6f} saniye
Optimize kod suresi: {yeni_sure:.6f} saniye
Hizlanma: {hizlanma:.2f} kat
Dogruluk testi: BASARILI

Kisa yorum: 
Eski fonksiyondaki iç içe 'for' döngüleri (O(N^2) karmaşıklık), kodu büyük verilerde çok yavaşlatıyordu. 
Optimize edilmiş fonksiyonda Python'ın 'set()' (küme) veri yapısı kullanılarak zaman karmaşıklığı O(N) seviyesine indirildi. 
Bu sayede eleman arama işlemleri hızlandı ve kodun sonucu aynı kalırken çalışma süresinde devasa bir hızlanma elde edildi.
"""

with open("performans_raporu.txt", mode="w", encoding="utf-8") as dosya:
    dosya.write(rapor_metni)

print("\n'performans_raporu.txt' başarıyla oluşturuldu!")