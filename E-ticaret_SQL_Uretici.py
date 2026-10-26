"""
Yapay Zekâ Destekli Doğal Dilden SQL Üretici
Yapay-Zeka-ile-Proglamlama deposundaki E-ticaret.py dosyasından bağımsızdır.

Kurulum:
    pip install google-genai

Windows PowerShell:
    $env:GEMINI_API_KEY="GEMINI_API_ANAHTARINIZ"
    python E-ticaret_SQL_Uretici.py

macOS / Linux:
    export GEMINI_API_KEY="GEMINI_API_ANAHTARINIZ"
    python E-ticaret_SQL_Uretici.py
"""

import os
import sys

from google import genai
from google.genai import errors


MODEL_ADI = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Görseldeki örnekte kullanılan veritabanı şeması
schema = """
1. Musteriler Tablosu: musteri_id, ad_soyad, eposta, sehir
2. Siparisler Tablosu: siparis_id, musteri_id, tutar, siparis_tarihi
"""

# Yeni talep: Farklı sorgular denemek için bu metni değiştirebilirsin.
talep = """
Son 30 günde 5000 TL üzeri alışveriş yapan İstanbul'daki
müşterilerin adını, e-posta adresini ve toplam harcama tutarını getir.
"""


def sql_uret(veritabani_semasi: str, kullanici_talebi: str) -> str:
    """Gemini'ye şema ve talebi gönderir, üretilen SQL metnini döndürür."""
    api_anahtari = os.getenv("GEMINI_API_KEY")
    if not api_anahtari:
        raise RuntimeError(
            "GEMINI_API_KEY ortam değişkeni tanımlı değil.\n"
            "Gemini API anahtarını ortam değişkeni olarak tanımlayıp tekrar çalıştır."
        )

    client = genai.Client(api_key=api_anahtari)

    sistem_mesaji = """
Sen bir SQL uzmanısın. Verilen veritabanı şemasına ve kullanıcı talebine göre
tek bir PostgreSQL sorgusu üret.

Kurallar:
- Yalnızca SQL sorgusunu döndür; açıklama veya Markdown kod bloğu ekleme.
- Yalnızca şemada bulunan tablo ve sütun adlarını kullan.
- Müşteriler ile siparişleri musteri_id üzerinden JOIN ile birleştir.
- Toplam harcama için SUM(s.tutar) kullan ve müşteri bazında GROUP BY yap.
- Son 30 gün filtresinde s.siparis_tarihi >= CURRENT_DATE - INTERVAL '30 days' kullan.
- İstanbul filtresinde m.sehir = 'İstanbul' kullan.
- Toplam harcaması 5000 TL'den fazla olan müşterileri HAVING SUM(s.tutar) > 5000 ile filtrele.
- Sonuçta ad_soyad, eposta ve toplam_harcama alanlarını döndür.
"""

    interaction = client.interactions.create(
        model=MODEL_ADI,
        input=(
            f"{sistem_mesaji}\n\n"
            f"VERİTABANI ŞEMASI:\n{veritabani_semasi}\n\n"
            f"KULLANICI TALEBİ:\n{kullanici_talebi}"
        ),
    )

    sql = (interaction.output_text or "").strip()
    if not sql:
        raise ValueError("Gemini boş yanıt döndürdü.")

    # Olası Markdown kod çitlerini kaldır.
    if sql.startswith("```"):
        satirlar = sql.splitlines()
        if satirlar and satirlar[0].startswith("```"):
            satirlar = satirlar[1:]
        if satirlar and satirlar[-1].strip() == "```":
            satirlar = satirlar[:-1]
        sql = "\n".join(satirlar).strip()

    return sql


def main() -> int:
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
        sql = sql_uret(schema, talep)
        print("Gemini yanıtı alındı!")
    except errors.APIError as exc:
        print(f"\n[API HATASI] {exc}", file=sys.stderr)
        return 1
    except (RuntimeError, ValueError) as exc:
        print(f"\n[HATA] {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"\n[SİSTEM HATASI] {exc}", file=sys.stderr)
        return 1

    print("\n" + "=" * 78)
    print("                         ÜRETİLEN SQL SORGUSU")
    print("=" * 78)
    print(sql)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
