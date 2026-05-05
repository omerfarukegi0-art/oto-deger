import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Değerini Öğren", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. ANA ARKA PLAN */
    .stApp {
        background-color: #050505 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* 2. GÖRÜNÜRLÜK VE KUTUCUK TEMİZLİĞİ (KRİTİK BÖLÜM) */
    /* Selectbox (Model Yılı) içindeki yazıyı bembeyaz yap */
    [data-baseweb="select"] * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important; /* Ok simgesi için */
    }

    /* MultiSelect (Boya/Değişen) içindeki baloncukları ve siyahlıkları temizle */
    div[data-baseweb="tag"] {
        background-color: #FF0000 !important;
        border-radius: 5px !important;
    }
    div[data-baseweb="tag"] span {
        color: #FFFFFF !important;
    }

    /* Giriş kutularının arkasındaki tüm Streamlit gölgelerini yok et */
    div[data-baseweb="input"], div[data-baseweb="select"], .stNumberInput div, .stSelectbox div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Kutuların içini modern antrasit yap ve altın çerçeve ekle */
    input, [data-baseweb="select"] > div {
        background-color: #121212 !important;
        color: #FFFFFF !important;
        border: 1px solid #d4af37 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        font-weight: 600 !important;
    }

    /* Sayı girişindeki artı-eksi butonlarını tamamen gizle (Görüntüyü bozar) */
    button[step] { display: none !important; }

    /* 3. LÜKS KART */
    .luxury-card {
        background-color: #0a0a0a !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 25px !important;
        padding: 30px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.8);
    }

    /* 4. BAŞLIK: Bİ'EDERİ */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        color: #FFFFFF !important;
        font-size: 4.5rem !important;
        text-align: center;
        margin-bottom: 0px !important;
    }
    
    .gold-text { color: #d4af37 !important; font-weight: 700; letter-spacing: 5px; text-transform: uppercase; font-size: 0.8rem; }

    /* 5. FİYAT PANELİ */
    .price-box {
        background: linear-gradient(135deg, #d4af37 0%, #f2d06b 100%) !important;
        padding: 40px !important;
        border-radius: 20px !important;
        text-align: center !important;
        margin: 25px 0 !important;
    }
    
    .price-val { color: #000 !important; font-size: 4rem !important; font-weight: 800 !important; margin: 0; }

    /* 6. BUTON: Kırmızı Ateşleme */
    .stButton>button {
        background: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        border: none !important;
        text-transform: uppercase !important;
        width: 100% !important;
    }

    label { color: #d4af37 !important; font-weight: 700; font-size: 0.75rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZİ ---
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
st.markdown("<br><h1>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>", unsafe_allow_html=True)
st.markdown("<p class='gold-text' style='text-align: center;'>Gerçek Değerini Keşfedin</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Verilerini Yapıştırın", height=200)
    if st.button("ANALİZİ BAŞLAT"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("perfection_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("MEVCUT KİLOMETRE", value=50000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("BOYA", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("DEĞİŞEN", ["Kaput", "Bagaj", "Kapı"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERİNİ ÖĞREN")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        katsayi = 4.2 if v_yil > 2021 else 3.5
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (65000 if v_vites == "Otomatik" else -15000) - (v_hasar * 0.15 + len(v_boya)*9000 + len(v_degisen)*25000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:700; letter-spacing:2px; opacity:0.6; font-size:0.8rem;'>TAHMİNİ RAYİÇ BEDEL</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ SIFIRLA"):
        del st.session_state.data
        st.rerun()
