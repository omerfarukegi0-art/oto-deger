import streamlit as st
import pandas as pd
import numpy as np
import re

# --- TEMA AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | Ekspertiz", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, label, .stMarkdown, .stSelectbox, .stNumberInput, .stRadio {
        color: #000000 !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .luxury-card {
        background: #FFFFFF;
        border: 3px solid #000000;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 10px 10px 0px #FF0000;
    }
    .price-box {
        background-color: #FFCC00;
        padding: 20px;
        border-radius: 15px;
        border: 4px solid #000000;
        text-align: center;
        margin: 20px 0;
        box-shadow: 8px 8px 0px #FF0000;
    }
    .price-val { color: #000000; font-size: 4.5rem; font-weight: 900; margin: 0; line-height: 1; }
    .stButton>button {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: 800;
        border-radius: 10px;
        border: 3px solid #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ MOTORU ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    kms = [int(k.replace(".", "")) for k in re.findall(r"\b(\d{1,3}\.\d{3})\b", metin)]
    limit = min(len(fiyatlar), len(yillar), len(kms))
    return pd.DataFrame({"Yıl": yillar[:limit], "KM": kms[:limit], "Fiyat": fiyatlar[:limit]}).drop_duplicates()

# --- PARÇA LİSTESİ ---
ekspertiz_parcalari = [
    "Kaput", "Tavan", "Bagaj Kapağı", 
    "Ön Tampon", "Arka Tampon",
    "Sağ Ön Çamurluk", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamurluk",
    "Sol Ön Çamurluk", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamurluk"
]

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center; font-size: 5rem; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000; font-weight: 900; font-size: 1.2rem; margin-top:-20px;'>🏁 DETAYLI EKSPERTİZ VE DEĞERLEME</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Verilerini Yapıştır", height=200, placeholder="Sahibinden metnini buraya yapıştırın...")
    if st.button("🚀 PİYASAYI ANALİZ ET"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- DETAY FORMU ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("pro_ekspertiz_form"):
        st.markdown("<h3 style='margin-top:0;'>🔍 Araç Detayları ve Ekspertiz</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=100000, step=1000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with c2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ekspertiz_parcalari)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ekspertiz_parcalari)
        
        st.write("")
        submit = st.form_submit_button("💰 HESAPLA VE RAPORLA")

    if submit:
        df = st.session_state.data
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        
        # Kaporta Kaybı Hesaplama (Parça başına piyasa etkisi)
        # Tavan ve Kaput boyası fiyattan daha çok düşer
        ozel_parcalar = ["Tavan", "Kaput", "Bagaj Kapağı"]
        boya_kaybi = sum([40000 if p in ozel_parcalar else 20000 for p in v_boya])
        degisen_kaybi = sum([80000 if p in ozel_parcalar else 45000 for p in v_degisen])
        
        final_price = baz + (df["KM"].mean() - v_km)*2.8 + (85000 if v_vites == "Otomatik" else 0) - (v_hasar*0.9 + boya_kaybi + degisen_kaybi)

        st.markdown(f"<div class='price-box'><p class='price-val'>{max(0, final_price):,.0f} TL</p></div>", unsafe_allow_html=True)

        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        res = [
            ("Model Baz Fiyatı", f"{baz:,.0f} TL"),
            ("Kilometre Etkisi", f"{(df['KM'].mean() - v_km)*2.8:+,.0f} TL"),
            ("Ekspertiz Düşümü (Boya/Değişen)", f"-( {boya_kaybi + degisen_kaybi:,.0f} ) TL"),
            ("Hızlı Satış (Acil)", f"{(final_price * 0.91):,.0f} TL")
        ]
        for label, val in res:
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #eee;'><span style='color:#FF0000; font-weight:800;'>{label}</span><span style='font-weight:700;'>{val}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE VE BAŞTAN BAŞLA"):
        del st.session_state.data
        st.rerun()
