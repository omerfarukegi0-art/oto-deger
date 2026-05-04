import streamlit as st
import pandas as pd
import numpy as np
import re

# --- PRESTİJ AYARLARI ---
st.set_page_config(page_title="Bİ'EDERİ | Elite", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. OLED BLACK ARKA PLAN */
    .stApp {
        background-color: #000000 !important;
        background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #000000 70%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* 2. SİYAH KUTUCUKLARI VE STANDART GÖLGELERİ YOK ETME PROTOKOLÜ */
    /* Streamlit'in tüm iskeletini şeffaflaştırıyoruz */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"],
    .stNumberInput div, .stSelectbox div, .stMultiSelect div, [data-testid="stForm"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* 3. LÜKS GİRİŞ ALANLARI (Custom UI) */
    input, div[role="combobox"], [data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.04) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.5s ease !important;
    }

    input:focus, div[role="combobox"]:focus {
        border-color: #FF0000 !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.2) !important;
    }

    /* 4. ANA KART: "Frozen Glass" */
    .luxury-card {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 40px !important;
        padding: 50px !important;
        backdrop-filter: blur(40px);
        box-shadow: 0 40px 100px rgba(0,0,0,0.8);
        margin-bottom: 30px;
    }

    /* 5. BAŞLIK: Ultra Minimal & Rich */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -4px !important;
        color: #FFFFFF !important;
        font-size: 6rem !important;
        margin-bottom: 0px !important;
    }
    
    .tagline {
        color: #FF0000 !important;
        letter-spacing: 12px !important;
        font-size: 0.7rem !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        opacity: 0.9;
        margin-top: -20px;
    }

    /* 6. FİYAT EKRANI: "Hyper-Focus" */
    .price-box {
        background: linear-gradient(135deg, #FFCC00 0%, #FF9900 100%) !important;
        padding: 60px 20px !important;
        border-radius: 40px !important;
        text-align: center !important;
        margin: 40px 0 !important;
        box-shadow: 0 30px 60px rgba(255, 153, 0, 0.2);
    }
    
    .price-val { 
        color: #000000 !important; 
        font-size: 6rem !important; 
        font-weight: 800 !important; 
        letter-spacing: -5px !important;
        line-height: 1;
    }

    /* 7. BUTON: "Ignition" */
    .stButton>button {
        background: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        border-radius: 25px !important;
        height: 4.5em !important;
        border: none !important;
        transition: 0.5s cubic-bezier(0.19, 1, 0.22, 1) !important;
        text-transform: uppercase !important;
        font-size: 1rem !important;
    }

    .stButton>button:hover {
        background: #FFFFFF !important;
        color: #FF0000 !important;
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(255, 255, 255, 0.2);
    }
    
    /* Etiketler */
    label { color: rgba(255,255,255,0.4) !important; font-weight: 600 !important; font-size: 0.75rem !important; letter-spacing: 1px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ANALİZ MOTORU ---
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
st.markdown("<br><h1 style='text-align: center;'>Bİ'EDERİ</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline' style='text-align: center;'>Elite Asset Valuation</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,0.4); font-size:0.8rem; letter-spacing:2px;'>MARKET DATA FEED</p>", unsafe_allow_html=True)
    raw_input = st.text_area("", height=200, placeholder="Piyasa verilerini buraya aktarın...")
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
    with st.form("elite_form"):
        st.markdown("<p style='color:#FF0000; font-weight:800; font-size:0.8rem; letter-spacing:3px;'>01. ARAÇ PARAMETRELERİ</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER (TL)", value=0, step=1000)
            v_boya = st.multiselect("BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERİ HESAPLA")

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
                <p style='color:#000; font-weight:700; letter-spacing:5px; opacity:0.5; font-size:0.7rem; margin-bottom:10px;'>RAYİÇ BEDEL</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} <span style='font-size:1.5rem; letter-spacing:0;'>TL</span></h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
