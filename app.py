import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARI ---
st.set_page_config(page_title="OTO-DEĞER", layout="wide")

# --- VERİ AYRIŞTIRMA ---
def veriyi_ayristir(metin):
    # Fiyatları bul (Örn: 1.250.000 TL)
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    # Yılları bul (2000-2026 arası)
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    # Kilometreleri bul (Noktalı sayılar)
    kms = []
    km_adaylari = re.findall(r"\b(\d{1,3}[\.,]\d{3})\b", metin)
    for k in km_adaylari:
        sayi = int(k.replace(".", "").replace(",", ""))
        if 500 < sayi < 600000 and sayi not in fiyatlar:
            kms.append(sayi)
            
    limit = min(len(fiyatlar), len(yillar), len(kms))
    if limit == 0: return pd.DataFrame()
    
    df = pd.DataFrame({
        "Yıl": yillar[:limit], 
        "Fiyat": fiyatlar[:limit], 
        "KM": kms[:limit]
    })
    return df.drop_duplicates()

# --- ANA EKRAN ---
st.title("🚗 OTO-DEĞER: Akıllı Piyasa Analizi")
st.write("Sahibinden'den kopyaladığınız ilan listesini yapıştırın ve analizi başlatın.")

if 'data' not in st.session_state:
    # Veri Giriş Alanı
    raw_input = st.text_area("İlan Metnini Buraya Yapıştırın", height=300)
    if st.button("Piyasayı Analiz Et"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
            else:
                st.error("Veri okunamadı. Lütfen liste görünümünde kopyaladığınızdan emin olun.")
else:
    df = st.session_state.data
    
    # Özet İstatistikler
    col1, col2, col3 = st.columns(3)
    avg_price = df["Fiyat"].mean()
    col1.metric("Ortalama Fiyat", f"{avg_price:,.0f} TL")
    col2.metric("Analiz Edilen İlan", len(df))
    col3.metric("En Uygun Fiyat", f"{df['Fiyat'].min():,.0f} TL")

    st.divider()

    # Filtreleme ve Fırsatlar
    st.subheader("🌟 Fırsat Olabilir (Ortalama Altı İlanlar)")
    firsatlar = df[df["Fiyat"] < avg_price].sort_values(by="Fiyat")
    st.dataframe(firsatlar, use_container_width=True)

    # Grafik
    st.subheader("📉 Fiyat - KM Dağılımı")
    st.scatter_chart(df, x="KM", y="Fiyat", color="Yıl")

    if st.button("🔄 Yeni Analiz Başlat"):
        del st.session_state.data
        st.rerun()
