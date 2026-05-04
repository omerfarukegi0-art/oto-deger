import streamlit as st
import pandas as pd
import numpy as np
import re

# --- LÜKS TEMA VE RENK AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | Sport", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* Arka Plan: Koyu Antrasit ve Gece Mavisi Gradyan */
    .stApp {
        background: radial-gradient(circle at top right, #1e2229, #0f1115) !important;
    }

    /* Tüm Yazılar Beyaz ve Okunaklı (Koyu temaya uygun) */
    h1, h2, h3, p, label, span, .stMarkdown, .stSelectbox, .stNumberInput, .stRadio {
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Kartlar: Şeffaf (Glassmorphism) ve Kırmızı Vurgulu */
    .luxury-card {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        padding: 30px !important;
        margin-bottom: 25px !important;
        backdrop-filter: blur(10px);
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5), 0px 5px 0px #FF0000 !important;
    }

    /* Fiyat Paneli: Parlayan Sarı */
    .price-box {
        background: linear-gradient(135deg, #FFCC00 0%, #FFAA00 100%) !important;
        padding: 35px !important;
        border-radius: 20px !important;
        text-align: center !important;
        margin: 25px 0 !important;
        box-shadow: 0px 0px 20px rgba(255, 204, 0, 0.3);
    }
    
    .price-label { 
        color: #000000 !important; 
        font-weight: 900 !important; 
        letter-spacing: 2px !important; 
        text-transform: uppercase;
        margin-bottom: 5px !important;
        opacity: 0.8;
    }
    
    .price-val { 
        color: #000000 !important; 
        font-size: 5rem !important; 
        font-weight: 900 !important; 
        line-height: 1 !important;
    }

    /* Kırmızı Aksiyon Butonu */
    .stButton>button {
        background: linear-gradient(90deg, #FF0000 0%, #B20000 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        border: none !important;
        height: 3.8em !important;
        text-transform: uppercase !important;
        box-shadow: 0px 4px 15px rgba(255, 0, 0, 0.3) !important;
        transition: 0.3s !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0px 6px 20px rgba(255, 0, 0, 0.5) !important;
    }

    /* Input Alanlarını Koyu Temaya Uydurma */
    input, .stSelectbox > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
st.markdown("<br><h1 style='text-align: center; font-size: 5.5rem; font-weight: 900; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000 !important; font-weight: 800; font-size: 1.2rem; margin-top:-25px; letter-spacing: 4px;'>ULTIMATE ANALYTICS</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📋 İlan Listesi Girişi</h3>", unsafe_allow_html=True)
    raw_input = st.text_area("", height=200, placeholder="Verileri buraya aktarın...")
    if st.button("🚀 ANALİZİ BAŞLAT"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- FORM ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("midnight_form"):
        st.markdown("<h3 style='margin-top:0;'>🔍 Kondisyon Girişi</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYALI", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        submit = st.form_submit_button("💰 DEĞERLEME YAP")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        
        if len(yil_verisi) >= 2:
            katsayi, _ = np.polyfit(yil_verisi["KM"], yil_verisi["Fiyat"], 1)
            final_katsayi = abs(katsayi) if katsayi < 0 else 3.8
        else:
            final_katsayi = 4.5 if v_yil > 2021 else 3.5

        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz_fiyat = np.poly1d(z)(v_yil)
        
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        km_bonusu = (km_ort - v_km) * final_katsayi
        
        final_price = (baz_fiyat * 1.05) + km_bonusu + (65000 if v_vites == "Otomatik" else -15000) - (v_hasar * 0.18 + len(v_boya)*8500 + len(v_degisen)*19000)

        # --- SONUÇ ---
        st.markdown(f"""
            <div class='price-box'>
                <p class='price-label'>Tahmini Rayiç Değer</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 YENİ ANALİZ"):
        del st.session_state.data
        st.rerun()
