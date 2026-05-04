import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bİ'EDERİ | Değerini Öğren", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. ANA ARKA PLAN (Streamlit Dark ile Uyumlu) */
    .stApp {
        background-color: #0e1117 !important;
    }

    /* 2. KUTULARI ARKA PLANLA EŞİTLEME (Görünmezlik Protokolü) */
    /* Tüm giriş alanlarını arka plan rengiyle aynı yapıyoruz */
    input, div[data-baseweb="select"], div[data-baseweb="input"], .stNumberInput div, .stSelectbox div {
        background-color: #161b22 !important; 
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
    }

    /* Odaklanınca sadece alt çizgi yansın */
    input:focus {
        border-bottom: 2px solid #FFCC00 !important;
    }

    /* 3. LÜKS KART TASARIMI */
    .luxury-card {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 24px !important;
        padding: 35px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border-left: 5px solid #FF0000 !important;
    }

    /* Metin Renkleri */
    h1, h2, h3, p, label {
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    label { opacity: 0.6; font-size: 0.8rem !important; letter-spacing: 1px; }

    /* 4. FİYAT PANELİ */
    .price-box {
        background: linear-gradient(135deg, #FFCC00 0%, #FFAA00 100%) !important;
        padding: 40px !important;
        border-radius: 25px !important;
        text-align: center !important;
        box-shadow: 0 0 30px rgba(255, 204, 0, 0.2);
    }
    
    .price-val { color: #000 !important; font-size: 4.5rem !important; font-weight: 900 !important; margin: 0; }

    /* 5. ANA BUTON */
    .stButton>button {
        background: linear-gradient(90deg, #FF0000 0%, #B20000 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 15px !important;
        height: 3.8em !important;
        border: none !important;
        text-transform: uppercase !important;
        width: 100% !important;
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
st.markdown("<br><h1 style='text-align: center; font-size: 4.5rem;'>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FFCC00; font-weight: 800; letter-spacing: 4px; margin-top:-25px;'>PREMIUM ANALİZ SİSTEMİ</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📊 Veri Girişi</h3>", unsafe_allow_html=True)
    raw_input = st.text_area("", height=200, placeholder="İlanları buraya aktarın...")
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
    with st.form("blended_form"):
        st.markdown("<h3 style='margin-top:0; color:#FF0000;'>📋 Araç Detayları</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("🛣️ KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("💸 TRAMER KAYDI (TL)", value=0, step=1000)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yan Kapılar", "Çamurluklar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("ARACIMIN DEĞERİNİ ÖĞREN")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        katsayi = 4.2 if v_yil > 2021 else 3.5
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (65000 if v_vites == "Otomatik" else -15000) - (v_hasar * 0.18 + len(v_boya)*9000 + len(v_degisen)*22000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:800; letter-spacing:2px; opacity:0.7;'>TAHMİNİ SATIŞ FİYATI</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
