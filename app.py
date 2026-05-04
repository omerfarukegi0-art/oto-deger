import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- TEMA VE TASARIM AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | Görsel Ekspertiz", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #FFFFFF; }
    .luxury-card {
        background: #FFFFFF; border: 3px solid #000000; border-radius: 20px;
        padding: 30px; margin-bottom: 25px; box-shadow: 10px 10px 0px #FF0000;
    }
    .price-box {
        background-color: #FFCC00; padding: 20px; border-radius: 15px;
        border: 4px solid #000000; text-align: center; margin: 20px 0; box-shadow: 8px 8px 0px #FF0000;
    }
    .price-val { color: #000000; font-size: 4rem; font-weight: 900; margin: 0; }
    
    /* Araç Şeması CSS */
    .car-container { text-align: center; margin-top: 20px; position: relative; }
    .svg-car { width: 300px; height: auto; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZ MOTORU ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    limit = min(len(fiyatlar), len(yillar))
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit]}).drop_duplicates()

# --- ŞEMA PARÇALARI ---
parca_haritasi = {
    "Kaput": "M 100,50 L 200,50 L 190,120 L 110,120 Z",
    "Tavan": "M 115,150 L 185,150 L 180,230 L 120,230 Z",
    "Bagaj": "M 110,310 L 190,310 L 200,380 L 100,380 Z",
    "Sol Ön Çamur.": "M 60,60 L 90,60 L 100,120 L 70,120 Z",
    "Sağ Ön Çamur.": "M 210,60 L 240,60 L 230,120 L 200,120 Z",
    "Sol Ön Kapı": "M 75,130 L 105,130 L 110,210 L 80,210 Z",
    "Sağ Ön Kapı": "M 195,130 L 225,130 L 220,210 L 190,210 Z",
    "Sol Arka Kapı": "M 80,220 L 110,220 L 115,290 L 85,290 Z",
    "Sağ Arka Kapı": "M 190,220 L 220,220 L 215,290 L 185,290 Z",
    "Sol Arka Çamur.": "M 70,300 L 100,300 L 90,370 L 60,370 Z",
    "Sağ Arka Çamur.": "M 200,300 L 230,300 L 240,370 L 210,370 Z"
}

# --- HEADER ---
st.markdown("<h1 style='text-align: center; font-size: 4rem;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Verilerini Yapıştır", height=200)
    if st.button("🚀 PİYASAYI ÇÖZ"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- DETAY FORMU ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("visual_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
            v_hasar = st.number_input("TRAMER (TL)", value=0)
        with col2:
            v_boya = st.multiselect("🎨 BOYA (Sarı)", list(parca_haritasi.keys()))
            v_degisen = st.multiselect("🛠️ DEĞİŞEN (Kırmızı)", list(parca_haritasi.keys()))
            v_renk = st.selectbox("DIŞ RENK", ["Standart", "Lansman Rengi (+)", "Özel Renk (++)"])
        
        submit = st.form_submit_button("💰 HESAPLA VE ŞEMAYI ÇİZ")

    if submit:
        # Hesaplama Motoru (Dengeli Mod)
        df = st.session_state.data
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        
        boya_kaybi = sum([20000 if p in ["Tavan", "Kaput"] else 10000 for p in v_boya])
        degisen_kaybi = sum([45000 if p in ["Tavan", "Kaput"] else 25000 for p in v_degisen])
        final_price = baz + (60000 if v_vites == "Otomatik" else 0) - (v_hasar*0.2 + boya_kaybi + degisen_kaybi)

        # GÖRSEL ŞEMA ÇİZİMİ (SVG)
        svg_code = f'<svg viewBox="0 0 300 450" class="svg-car" xmlns="http://w3.org">'
        # Arka plan hatları
        svg_code += '<rect x="50" y="20" width="200" height="410" rx="40" fill="none" stroke="#ddd" stroke-width="2"/>'
        
        for parca, path in parca_haritasi.items():
            color = "#EEEEEE" # Varsayılan gri
            if parca in v_degisen: color = "#FF0000" # Kırmızı
            elif parca in v_boya: color = "#FFCC00" # Sarı
            svg_code += f'<path d="{path}" fill="{color}" stroke="#000" stroke-width="1.5" />'
        
        svg_code += '</svg>'
        
        st.markdown("<div class='car-container'>", unsafe_allow_html=True)
        st.write("### 🚗 EKSPERTİZ GÖRÜNÜMÜ")
        st.markdown(svg_code, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='price-box'><p class='price-val'>{max(0, final_price):,.0f} TL</p></div>", unsafe_allow_html=True)

    if st.button("🔄 BAŞTAN BAŞLA"):
        del st.session_state.data
        st.rerun()
