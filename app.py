import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- PRESTİJ AYARLARI ---
st.set_page_config(page_title="VALUATE-PRO | Luxury", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. ANA TEMA: Gece Siyahı */
    .stApp {
        background-color: #050505 !important;
        background-image: radial-gradient(circle at top right, #1a1a1a, #050505) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 2. TÜM YAZILAR: Beyaz ve Altın Dengesi */
    h1, h2, h3, p, span, div, .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Başlıklar Altın Rengi */
    label {
        color: #d4af37 !important; /* Altın Sarısı */
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.8rem !important;
    }

    /* 3. GİRİŞ KUTULARI: Altın Çerçeveli ve Net */
    input, div[data-baseweb="select"] > div {
        background-color: #121212 !important;
        color: #ffffff !important;
        border: 1px solid #d4af37 !important; /* Altın Çerçeve */
        border-radius: 10px !important;
        height: 48px !important;
        font-weight: 600 !important;
    }
    
    /* Seçim kutusundaki yazıyı bembeyaz yap */
    div[data-baseweb="select"] span { color: white !important; }

    /* 4. PREMİUM KART: Altın Detaylı */
    .luxury-card {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 24px !important;
        padding: 40px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    }

    /* 5. FİYAT PANELİ: Altın Gradyan */
    .price-box {
        background: linear-gradient(135deg, #d4af37 0%, #f2d06b 50%, #aa8a2e 100%) !important;
        padding: 45px !important;
        border-radius: 30px !important;
        text-align: center !important;
        margin: 30px 0 !important;
        box-shadow: 0 0 40px rgba(212, 175, 55, 0.3);
    }
    
    .price-val { 
        font-family: 'Orbitron', sans-serif !important;
        font-size: 4.5rem !important; 
        font-weight: 900 !important; 
        letter-spacing: -2px !important;
        margin: 0 !important;
        color: #000000 !important; /* Siyah font altın üzerinde çok net durur */
    }

    /* 6. BUTON: Yarış Kırmızısı */
    .stButton>button {
        background: linear-gradient(90deg, #FF0000 0%, #b91c1c 100%) !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-family: 'Orbitron', sans-serif !important;
        border-radius: 12px !important;
        border: none !important;
        height: 4em !important;
        text-transform: uppercase !important;
        width: 100% !important;
        box-shadow: 0 10px 20px rgba(255, 0, 0, 0.2) !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 30px rgba(255, 0, 0, 0.4) !important;
        background: #FF0000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ANALİZ MOTORU ---
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

# --- BAŞLIK ---
st.markdown("<br><h1 style='text-align: center; font-size: 4rem; font-family:Orbitron;'>VALUATE-<span style='color:#FF0000'>PRO</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #d4af37; letter-spacing: 6px; margin-top: -20px; font-weight:700;'>GOLDEN ASSET INTELLIGENCE</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#d4af37;'>📥 Market Verisi Aktarımı</h3>", unsafe_allow_html=True)
    raw_input = st.text_area("", height=200, placeholder="İlanları buraya kopyalayın...")
    if st.button("ANALİZ MOTORUNU ATEŞLE"):
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
        st.markdown("<h3 style='color:#FF0000; font-family:Orbitron;'>KONFİGÜRASYON</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("MEVCUT KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0, step=1000)
            v_boya = st.multiselect("BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("X-RAY DEĞERLEMEYİ YAP")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        katsayi = 4.5 if v_yil > 2022 else 3.8
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (70000 if v_vites == "Otomatik" else -20000) - (v_hasar * 0.15 + len(v_boya)*9500 + len(v_degisen)*25000)

        # --- SONUÇ ---
        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000000; font-weight:800; letter-spacing:2px; opacity:0.8; font-size:0.85rem;'>GÜNCEL PAZAR RAYİÇ BEDELİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 YENİ SORGULAMA"):
        del st.session_state.data
        st.rerun()
