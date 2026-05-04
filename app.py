import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- TEMA VE STİL ---
st.set_page_config(page_title="OTO-DEĞER | Dinamik Analiz", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span, .stMarkdown, .stSelectbox, .stNumberInput, .stRadio {
        color: #000000 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .luxury-card {
        background: #FFFFFF !important; border: 3px solid #000000;
        border-radius: 20px; padding: 30px; margin-bottom: 25px; box-shadow: 10px 10px 0px #FF0000;
    }
    .price-box {
        background-color: #FFCC00; padding: 25px; border-radius: 15px;
        border: 4px solid #000000; text-align: center; margin: 20px 0; box-shadow: 8px 8px 0px #FF0000;
    }
    .price-val { color: #000000 !important; font-size: 4rem; font-weight: 900; margin: 0; line-height: 1.1; }
    .stButton>button {
        background-color: #FF0000 !important; color: #FFFFFF !important;
        font-weight: 800; border-radius: 10px; border: 3px solid #000000; height: 3.5em; text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ AYRIŞTIRICI ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    kms = []
    km_adaylari = re.findall(r"\b(\d{1,3}[\.,]\d{3})\b", metin)
    for k in km_adaylari:
        sayi = int(k.replace(".", "").replace(",", ""))
        if 500 < sayi < 600000 and sayi not in fiyatlar:
            kms.append(sayi)
    
    limit = min(len(fiyatlar), len(yillar), len(kms))
    if limit == 0: return pd.DataFrame()
    df = pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]})
    return df.drop_duplicates()

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center; font-size: 4.5rem; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000 !important; font-weight: 900; font-size: 1.1rem; margin-top:-20px;'>🏁 İLAN BAZLI DİNAMİK HESAPLAMA</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini Yapıştır", height=200)
    if st.button("🚀 PİYASAYI ANALİZ ET"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    with st.form("dynamic_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("ARACININ KİLOMETRESİ", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYALI", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        submit = st.form_submit_button("💰 PİYASA ANALİZİYLE HESAPLA")

    if submit:
        df = st.session_state.data
        
        # --- 1. DİNAMİK KM KATSAYISI HESAPLAMA ---
        # Sadece seçilen yılın araçlarına bakarak pazarın "KM hassasiyetini" ölçer
        yil_verisi = df[df["Yıl"] == v_yil]
        
        if len(yil_verisi) >= 2:
            # Lineer Regresyon: Fiyat = (m * KM) + b -> Buradaki 'm' bizim dinamik katsayımızdır
            X = yil_verisi["KM"]
            y = yil_verisi["Fiyat"]
            katsayi, sabit = np.polyfit(X, y, 1)
            
            # Eğer katsayı mantıksızsa (örn: km arttıkça fiyat artıyorsa), genel veriye bak
            if katsayi >= 0:
                katsayi, _ = np.polyfit(df["KM"], df["Fiyat"], 1)
            
            # Hala pozitifse (veri çok bozuksa) 3.5 fallback kullan
            final_katsayi = abs(katsayi) if katsayi < 0 else 3.5
        else:
            # Yeterli veri yoksa genel veriden veya varsayılandan al
            final_katsayi = 4.0 if v_yil > 2020 else 3.0

        # --- 2. BAZ FİYAT VE DÜZELTME ---
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz_fiyat = np.poly1d(z)(v_yil)
        
        # KM Etkisi (Dinamik katsayı ile)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        km_farki = km_ort - v_km
        km_bonusu = km_farki * final_katsayi
        
        # Diğer kalemler
        vites_farki = 60000 if v_vites == "Otomatik" else -15000
        kesintiler = (v_hasar * 0.18) + (len(v_boya) * 10000) + (len(v_degisen) * 25000)
        
        final_price = (baz_fiyat * 1.04) + km_bonusu + vites_farki - kesintiler

        # --- SONUÇ ---
        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#FF0000; font-weight:800; margin:0;'>HESAPLANAN PAZAR DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
                <p style='margin:10px 0 0 0; font-size:0.85rem; color:#444;'>
                İlanlardan Hesaplanan KM Katsayısı: <b>{final_katsayi:.2f} TL/KM</b><br>
                (Yani her 5.000 KM için pazar etkisi: <b>{(final_katsayi * 5000):,.0f} TL</b>)
                </p>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE"):
        del st.session_state.data
        st.rerun()
