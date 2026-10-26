"""
Yapay Zekâ Destekli Doğal Dilden SQL Üretici
E-ticaret projesinden bağımsız, yalnızca SQL sorgusu üretir.

Kurulum:
    pip install google-genai

PowerShell:
    $env:GEMINI_API_KEY="API_ANAHTARINIZ"
    python Dogal_Dilden_SQL_Uretici.py
"""

import os
import sys
from google import genai
from google.genai import errors


MODEL_ADI = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

schema = """
1. Musteriler Tablosu: musteri_id, ad_soyad, eposta, sehir
2. Siparisler Tablosu: siparis_id, musteri_id, tutar, siparis_tarihi
"""

# Yeni kullanıcı talebi
talep = """
Son 30 günde 5000 TL üzeri alışveriş yapan İstanbul'daki
müşterilerin adını, e-posta adresini ve toplam harcama tutarını getir.
"""


def sql_uret(sema, kullanici_talebi):
    api_anahtari = os.getenv("GEMINI_API_KEY")
    if not api_anahtari:
        raise RuntimeError(
            "GEMINI_API_KEY bulunamadı. Önce API anahtarınızı ortam değişkeni olarak tanımlayın."
        )

    client = genai.Client(api_key=api_anahtari)

    prompt = f"""
Sen bir veritabanı uzmanısın. Aşağıdaki şema ve kullanıcı talebine göre
tek bir PostgreSQL SQL sorgusu üret.

Kurallar:
- Sadece SQL kodunu döndür; açıklama veya Markdown kod bloğu yazma.
- Şemada olmayan tablo ya da sütun kullanma.
- Musteriler ile Siparisler tablolarını musteri_id üzerinden JOIN ile bağla.
- Son 30 gün filtresi için s.siparis_tarihi >= CURRENT_DATE - INTERVAL '30 days' kullan.
- İstanbul filtresi için m.sehir = 'İstanbul' kullan.
- Müşteri başına toplam harcamayı SUM(s.tutar) ile hesapla.
- Müşteri bilgilerini ve toplamı seç; tüm seçili müşteri alanlarını GROUP BY içinde bulundur.
- Toplam harcaması 5000 TL'den büyük müşterileri HAVING SUM(s.tutar) > 5000 ile filtrele.
- Toplam harcama sütununa toplam_harcama adını ver.

VERİTABANI ŞEMASI:
{sema}

KULLANICI TALEBİ:
{kullanici_talebi}
"""

    yanit = client.models.generate_content(
        model=MODEL_ADI,
        contents=prompt,
    )
    sql = (yanit.text or "").strip()

    if not sql:
        raise ValueError("Gemini boş yanıt döndürdü.")

    # Kod çiti geldiyse kaldır.
    if sql.startswith("```"):
        satirlar = sql.splitlines()
        if satirlar and satirlar[0].startswith("```"):
            satirlar = satirlar[1:]
        if satirlar and satirlar[-1].strip() == "```":
            satirlar = satirlar[:-1]
        sql = "\n".join(satirlar).strip()

    return sql


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    print("=" * 78)
    print("             YAPAY ZEKA DESTEKLI DOGAL DILDEN SQL URETICI")
    print("=" * 78)
    print("\n[AŞAMA 1] VERİTABANI ŞEMASI VE KULLANICI TALEBİ ALINDI...")
    print("\n[AŞAMA 2] SQL ÇEVİRİSİ İÇİN GEMINI'YE BAĞLANILIYOR...")
    print("\nGemini isteği gönderiliyor...")

    try:
        sorgu = sql_uret(schema, talep)
        print("Gemini yanıtı alındı!")
    except errors.APIError as hata:
        print(f"\n[API HATASI] {hata}")
        return 1
    except (RuntimeError, ValueError) as hata:
        print(f"\n[HATA] {hata}")
        return 1
    except Exception as hata:
        print(f"\n[BEKLENMEYEN HATA] {hata}")
        return 1

    print("\n" + "=" * 78)
    print("                         ÜRETİLEN SQL SORGUSU")
    print("=" * 78)
    print(sorgu)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
