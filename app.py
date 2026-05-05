import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Değerini Öğren", layout="centered")

# --- TERTEMİZ VE GÜVENLİ TASARIM ---
st.markdown("""
    <style>
    /* Genel Arka Plan ve Yazı Rengi */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Başlık Stili */
    h1 {
        color: #FFFFFF !important;
        font-family: sans-serif;
        font-weight: 800;
        text-align: center;
        font-size: 4rem !important;
    }
    
    /* Lüks Kart Yapısı */
    .luxury-card {
        background-color: #161b22;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #30363d;
        border-left: 5px solid #FF0000;
        margin-bottom: 20px;
    }

    /* Fiyat Paneli */
    .price-box {
        background-color: #FFCC00;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    }
    
    .price-val {
        color: #000000;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
    }

    /* Buton */
    .stButton>button {
        background-color: #FF0000 !important;
        color: white !important;
        font-weight: 700 !important;
        width: 100%;
        height: 3.5em;
        border-radius: 10px;
        border: none;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZİ ---
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
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]}).drop_duplicates()

# --- LOGO ---
st.markdown("<h1>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#d4af37; font-weight:700;'>GERÇEK PİYASA DEĞERLEME</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini Buraya Yapıştırın", height=200)
    if st.button("ANALİZİ BAŞLAT"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("main_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=50000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("BOYA", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("DEĞİŞEN", ["Kaput", "Bagaj", "Kapı"])
        
        st.write("")
        submit = st.form_submit_button("DEĞERİNİ ÖĞREN")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        # Dengeli Hesaplama
        final_price = (baz * 1.05) + (km_ort - v_km) * 3.8 + (60000 if v_vites == "Otomatik" else -20000) - (v_hasar * 0.15 + len(v_boya)*8000 + len(v_degisen)*20000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000000; font-weight:700; opacity:0.7;'>TAHMİNİ SATIŞ FİYATI</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE"):
        del st.session_state.data
        st.rerun()
