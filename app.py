import streamlit as st
import pandas as pd
import numpy as np
import re

# --- PRESTİJ AYARLARI ---
st.set_page_config(page_title="Bİ'EDERİ | Stealth Luxury", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. ANA ARKA PLAN: OLED BLACK */
    .stApp {
        background-color: #000000 !important;
        background-image: radial-gradient(at 50% 0%, #111827 0%, #000000 70%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* 2. GİRİŞ KUTULARI: ULTRA MODERN & PÜRÜZSÜZ */
    /* Tüm o çirkin gölgeleri ve siyah kutuları yok eder */
    div[data-baseweb="input"], div[data-baseweb="select"], .stNumberInput div, .stSelectbox div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Giriş kutularının içini daha 'pahalı' bir gri yapıyoruz */
    input, div[role="combobox"], [data-baseweb="select"] > div {
        background-color: #0a0a0a !important;
        color: #FFFFFF !important;
        border: 1px solid #1f2937 !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease;
    }

    input:focus, div[role="combobox"]:focus {
        border-color: #C5A059 !important; /* Muted Gold */
        box-shadow: 0 0 10px rgba(197, 160, 89, 0.1) !important;
    }

    /* 3. LÜKS KART: Glassmorphism */
    .luxury-card {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 30px !important;
        padding: 40px !important;
        backdrop-filter: blur(20px);
        box-shadow: 0 40px 100px rgba(0,0,0,0.5);
        margin-top: 20px;
    }

    /* 4. BAŞLIK: Minimal & Güçlü */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        color: #FFFFFF !important;
        font-size: 4rem !important;
        text-align: center;
        margin-bottom: 5px !important;
    }

    .tagline {
        color: #C5A059 !important;
        letter-spacing: 6px !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        text-align: center;
        opacity: 0.8;
        margin-bottom: 30px;
    }

    /* 5. ETİKETLER (Labels) */
    label {
        color: #9ca3af !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        margin-bottom: 8px !important;
    }

    /* 6. FİYAT PANELİ: "The Vault" */
    .price-box {
        background: linear-gradient(135deg, #C5A059 0%, #947a45 100%) !important;
        padding: 45px !important;
        border-radius: 25px !important;
        text-align: center !important;
        margin: 25px 0 !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    .price-val { color: #000 !important; font-size: 4rem !important; font-weight: 800 !important; margin: 0; }

    /* 7. BUTON: Carbon Red */
    .stButton>button {
        background: #b91c1c !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 15px !important;
        height: 3.8em !important;
        border: none !important;
        text-transform: uppercase !important;
        width: 100% !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        background: #ef4444 !important;
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

# --- HEADER ---
st.markdown("<br><h1>Bİ'EDERİ</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>PREMIUM ASSET VALUATION</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 Market verilerini buraya bırakın", height=200)
    if st.button("SİSTEMİ BAŞLAT"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("stealth_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("MEVCUT KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0, step=1000)
            v_boya = st.multiselect("BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yan Kapılar", "Çamurluklar"])
            v_degisen = st.multiselect("DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERİNİ ÖĞREN")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        katsayi = 4.2 if v_yil > 2022 else 3.5
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (65000 if v_vites == "Otomatik" else -15000) - (v_hasar * 0.15 + len(v_boya)*8000 + len(v_degisen)*25000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:700; letter-spacing:2px; opacity:0.6; font-size:0.8rem;'>TAHMİNİ PAZAR DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
