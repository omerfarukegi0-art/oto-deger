import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- TEMA VE ARKA PLAN AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | Premium", layout="centered")

# Seçtiğim Premium Resim: Açık gri/mavi tonlarında ferah bir araç detayı
bg_img = "https://unsplash.com"

st.markdown(f"""
    <style>
    @import url('https://googleapis.com');
    
    /* ARKA PLANI KESİN OLARAK ZORLAYAN BLOK */
    .stApp {{
        background: url("{bg_img}") no-repeat center center fixed !important;
        background-size: cover !important;
    }}

    /* İÇERİĞİN ARKASINA ŞIK BİR BUĞU (BLUR) VE BEYAZLIK EKLER */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(255, 255, 255, 0.75) !important; /* Ferah beyazlık */
        backdrop-filter: blur(8px); /* Modern buğu efekti */
        z-index: -1;
    }}

    /* Tüm metinlerin rengini SİYAH ve net yapar */
    h1, h2, h3, p, label, span, .stMarkdown, .stSelectbox, .stNumberInput, .stRadio {{
        color: #000000 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700;
    }}

    /* Kartların arkasından resmin hafifçe sızmasını sağlar (Glassmorphism) */
    .luxury-card {{
        background: rgba(255, 255, 255, 0.85) !important;
        border: 2px solid #000000 !important;
        border-radius: 20px !important;
        padding: 30px !important;
        margin-bottom: 25px !important;
        box-shadow: 10px 10px 0px #FF0000 !important;
    }}

    /* Fiyat Paneli (Sarı Üzerine Siyah) */
    .price-box {{
        background-color: #FFCC00 !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border: 4px solid #000000 !important;
        text-align: center !important;
        margin: 20px 0 !important;
        box-shadow: 8px 8px 0px #FF0000 !important;
    }}

    .price-val {{ 
        color: #000000 !important; 
        font-size: 4.5rem !important; 
        font-weight: 900 !important; 
        line-height: 1 !important; 
    }}

    /* Kırmızı Butonlar */
    .stButton>button {{
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border: 3px solid #000000 !important;
        height: 3.5em !important;
        text-transform: uppercase !important;
        box-shadow: 4px 4px 0px #000 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- VERİ MOTORU ---
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
st.markdown("<h1 style='text-align: center; font-size: 5rem; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000 !important; font-weight: 900; font-size: 1.2rem; margin-top:-20px;'>🏁 DİNAMİK PİYASA ANALİZ MERKEZİ</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📋 İlan Listesini Yapıştır</h3>", unsafe_allow_html=True)
    raw_input = st.text_area("", height=200, placeholder="Sahibinden metnini buraya bırakın...")
    if st.button("🚀 PİYASAYI ANALİZ ET"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- ANALİZ FORMU ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("pro_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        submit = st.form_submit_button("💰 ANALİZİ TAMAMLA")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        
        # Dinamik KM Katsayısı (İlanlardaki KM/Fiyat oranına göre)
        if len(yil_verisi) >= 2:
            katsayi, _ = np.polyfit(yil_verisi["KM"], yil_verisi["Fiyat"], 1)
            final_katsayi = abs(katsayi) if katsayi < 0 else 3.5
        else:
            final_katsayi = 4.0 if v_yil > 2020 else 3.0

        # Baz Fiyat (Model Yılı Trendi)
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz_fiyat = np.poly1d(z)(v_yil)
        
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        km_bonusu = (km_ort - v_km) * final_katsayi
        
        final_price = (baz_fiyat * 1.04) + km_bonusu + (60000 if v_vites == "Otomatik" else -15000) - (v_hasar * 0.18 + len(v_boya)*8000 + len(v_degisen)*18000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#FF0000 !important; font-weight:800; margin:0;'>TAHMİNİ RAYİÇ BEDEL</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE"):
        del st.session_state.data
        st.rerun()
