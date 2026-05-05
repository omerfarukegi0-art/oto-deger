import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- PROFESYONEL AYARLAR ---
st.set_page_config(page_title="VALUATE-PRO", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. ANA TEMA: Koyu Füme (Gözü yormaz, zengin durur) */
    .stApp {
        background-color: #0f1116 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 2. TÜM YAZILARI BEYAZA ZORLA (Okunurluk Garantisi) */
    h1, h2, h3, p, label, span, div, .stMarkdown {
        color: #ffffff !important;
    }

    /* 3. GİRİŞ ALANLARI: Temiz ve Keskin */
    input, div[data-baseweb="select"] > div {
        background-color: #1c1f26 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        height: 45px !important;
    }
    
    /* Seçim kutusundaki yazıyı bembeyaz yap */
    div[data-baseweb="select"] span { color: white !important; }

    /* 4. PREMİUM KART TASARIMI */
    .luxury-card {
        background-color: #161920 !important;
        border: 1px solid #30363d !important;
        border-radius: 20px !important;
        padding: 35px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }

    /* 5. FİYAT PANELİ: Elektrik Mavisi */
    .price-box {
        background: linear-gradient(135deg, #0052D4 0%, #4364F7 100%) !important;
        padding: 40px !important;
        border-radius: 20px !important;
        text-align: center !important;
        margin: 25px 0 !important;
        box-shadow: 0 0 30px rgba(67, 100, 247, 0.3);
    }
    
    .price-val { 
        font-size: 4.5rem !important; 
        font-weight: 900 !important; 
        letter-spacing: -2px !important;
        margin: 0 !important;
        color: #ffffff !important;
    }

    /* 6. BUTON: Keskin ve Modern */
    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        height: 3.5em !important;
        text-transform: uppercase !important;
        width: 100% !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        background-color: #4364F7 !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZ MOTORU ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    kms = []
    km_candidates = re.findall(r"\b(\d{1,3}[\.,]\d{3})\b", metin)
    for k in km_candidates:
        val = int(k.replace(".", "").replace(",", ""))
        if 500 < val < 600000 and val not in fiyatlar:
            kms.append(val)
    limit = min(len(fiyatlar), len(yillar), len(kms))
    if limit == 0: return pd.DataFrame()
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]}).drop_duplicates()

# --- HEADER ---
st.markdown("<br><h1 style='text-align: center; font-size: 4rem; font-weight: 900;'>VALUATE-<span style='color:#4364F7'>PRO</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.6; letter-spacing: 5px; margin-top: -20px;'>PRECISION MARKET ANALYSIS</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("### 📋 Veri Girişi")
    raw_input = st.text_area("", height=200, placeholder="İlanları buraya kopyalayın...")
    if st.button("ANALİZİ BAŞLAT"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- FORM ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("pro_form"):
        st.markdown("<h3 style='margin-top:0;'>⚙️ Araç Konfigürasyonu</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("🛣️ KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("💸 TRAMER (TL)", value=0, step=1000)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERLEMEYİ TAMAMLA")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        katsayi = 4.2 if v_yil > 2021 else 3.5
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (65000 if v_vites == "Otomatik" else -15000) - (v_hasar * 0.18 + len(v_boya)*9000 + len(v_degisen)*22000)

        # --- SONUÇ ---
        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#ffffff; font-weight:700; letter-spacing:2px; opacity:0.8; font-size:0.8rem;'>TAHMİNİ PAZAR DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 YENİ ANALİZ"):
        del st.session_state.data
        st.rerun()
