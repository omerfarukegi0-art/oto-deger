import streamlit as st
import pandas as pd
import numpy as np
import re

# --- PRESTİJ AYARLARI ---
st.set_page_config(page_title="Bİ'EDERİ | Ultra-Premium", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. ANA ARKA PLAN: Derin Antrasit ve Safir Geçişi */
    .stApp {
        background: radial-gradient(circle at top right, #1a1c23, #08090a) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 2. SİYAH KUTUCUKLARI VE VARSAYILAN GÖLGELERİ YOK ETME */
    div[data-baseweb="input"], div[data-baseweb="select"], .stNumberInput div, .stSelectbox div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* 3. LÜKS GİRİŞ ALANLARI: Kartla Bütünleşik */
    input, div[role="combobox"], [data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 15px !important;
        padding: 14px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }

    input:focus {
        background-color: rgba(255, 255, 255, 0.07) !important;
        border-color: #FF0000 !important;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.2) !important;
    }

    /* 4. ELMAS KESİM KART TASARIMI */
    .luxury-card {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 35px !important;
        padding: 50px !important;
        backdrop-filter: blur(25px);
        box-shadow: 0 30px 60px rgba(0,0,0,0.4);
        margin-top: 20px;
    }

    /* 5. BAŞLIKLAR: Modern & Pahalı */
    h1 {
        font-weight: 900 !important;
        letter-spacing: -3px !important;
        background: linear-gradient(to right, #FFFFFF, #888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 5.5rem !important;
    }

    .sub-brand {
        color: #FF0000 !important;
        letter-spacing: 10px !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        margin-top: -30px;
        opacity: 0.8;
    }

    /* 6. FİYAT PANELİ: "The Golden Vault" */
    .price-box {
        background: linear-gradient(135deg, #FFCC00 0%, #FFAA00 100%) !important;
        padding: 50px 20px !important;
        border-radius: 30px !important;
        text-align: center !important;
        margin: 40px 0 !important;
        box-shadow: 0 20px 40px rgba(255, 204, 0, 0.2);
    }
    
    .price-val { 
        color: #000000 !important; 
        font-size: 5rem !important; 
        font-weight: 900 !important; 
        letter-spacing: -2px !important;
    }

    /* 7. BUTON: Red Velvet */
    .stButton>button {
        background: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border-radius: 18px !important;
        height: 4.5em !important;
        border: none !important;
        transition: 0.4s !important;
        width: 100% !important;
        text-transform: uppercase !important;
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(255, 0, 0, 0.4);
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

# --- BAŞLIK ---
st.markdown("<br><h1 style='text-align: center;'>Bİ'EDERİ</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-brand' style='text-align: center;'>Professional Automotive Assets</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666; font-size:0.9rem;'>MARKET INTELLIGENCE DATA GİRİŞİ</p>", unsafe_allow_html=True)
    raw_input = st.text_area("", height=200, placeholder="İlan havuzunu buraya kopyalayın...")
    if st.button("SİSTEMİ AKTİVE ET"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("luxury_form"):
        st.markdown("<p style='color:#FF0000; font-weight:700; margin-bottom:20px;'>VEHICLE CONFIGURATION</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("📅 MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("🛣️ KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("💸 TRAMER (TL)", value=0, step=1000)
            v_boya = st.multiselect("🎨 BOYA", ["Kaput", "Tavan", "Bagaj", "Kapılar", "Çamurluklar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERLEMEYİ GERÇEKLEŞTİR")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        katsayi = 4.5 if v_yil > 2022 else 3.8
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (70000 if v_vites == "Otomatik" else -20000) - (v_hasar * 0.15 + len(v_boya)*9000 + len(v_degisen)*25000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:700; letter-spacing:4px; opacity:0.6; font-size:0.8rem;'>ESTIMATED MARKET VALUE</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 YENİ EKSPERTİZ"):
        del st.session_state.data
        st.rerun()
