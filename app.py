import streamlit as st
import pandas as pd
import numpy as np
import re

# --- LÜKS TEMA AYARLARI ---
st.set_page_config(page_title="Bİ'EDERİ | Luxury Valuation", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. ANA ARKA PLAN: Derin Safir/Lacivert */
    .stApp {
        background-color: #050b1a !important;
        background-image: radial-gradient(at 0% 0%, rgba(20, 30, 70, 0.5) 0, transparent 50%), 
                          radial-gradient(at 50% 0%, rgba(10, 20, 50, 0.5) 0, transparent 50%) !important;
    }

    /* 2. LOGO: "Bİ'EDERİ" - Antik Altın Rengi */
    h1 {
        font-family: 'Cinzel', serif !important;
        color: #d4af37 !important;
        font-size: 4.5rem !important;
        text-align: center;
        margin-bottom: 0px !important;
        letter-spacing: 5px !important;
        text-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }

    /* 3. LÜKS KART: Şampanya Grisi Zemin */
    .luxury-card {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        backdrop-filter: blur(15px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        margin-bottom: 25px;
    }

    /* 4. GİRİŞ KUTULARI: Kesin Görünürlük Protokolü */
    /* Tüm seçim ve sayı kutularının içini Lacivert yap, yazıları BEYAZ yap */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"],
    .stNumberInput div, .stSelectbox div {
        background-color: #0f172a !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 10px !important;
    }

    /* Kutu içindeki yazıları BEYAZA zorla */
    input, [data-baseweb="select"] * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 500 !important;
    }

    /* Başlıklar (Labels) - Altın Rengi */
    label {
        color: #d4af37 !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        letter-spacing: 1.5px !important;
    }

    /* 5. FİYAT PANELİ: "The Golden Vault" */
    .price-box {
        background: linear-gradient(145deg, #d4af37, #aa8a2e) !important;
        padding: 50px 20px !important;
        border-radius: 20px !important;
        text-align: center !important;
        box-shadow: 0 15px 35px rgba(212, 175, 55, 0.2);
        margin-top: 30px;
    }
    
    .price-val { 
        color: #050b1a !important; 
        font-size: 4rem !important; 
        font-weight: 800 !important; 
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        margin: 0;
    }

    /* 6. BUTON: Safir Mavi */
    .stButton>button {
        background: transparent !important;
        color: #d4af37 !important;
        border: 2px solid #d4af37 !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        transition: all 0.4s !important;
        text-transform: uppercase !important;
        width: 100% !important;
    }

    .stButton>button:hover {
        background: #d4af37 !important;
        color: #050b1a !important;
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.3);
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
st.markdown("<p style='text-align: center; color: #64748b; letter-spacing: 3px; font-size: 0.8rem; margin-top: -10px;'>PRECISION AUTOMOTIVE ANALYTICS</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 Market Verilerini Buraya Aktarın", height=150)
    if st.button("SİSTEMİ BAŞLAT"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- FORM ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("royal_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("🛣️ MEVCUT KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("💸 TRAMER KAYDI (TL)", value=0, step=1000)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERLEMEYİ OLUŞTUR")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        katsayi = 4.2 if v_yil > 2022 else 3.8
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (65000 if v_vites == "Otomatik" else -15000) - (v_hasar * 0.15 + len(v_boya)*9000 + len(v_degisen)*25000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#050b1a; font-weight:700; letter-spacing:2px; opacity:0.8; font-size:0.8rem; margin-bottom: 5px;'>GÜNCEL VARLIK DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 YENİ ANALİZ"):
        del st.session_state.data
        st.rerun()
