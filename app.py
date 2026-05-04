import streamlit as st
import pandas as pd
import numpy as np
import re

# --- TEMA VE STİL ---
st.set_page_config(page_title="OTO-DEĞER | Ekspertiz", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .luxury-card {
        background: #FFFFFF; border: 3px solid #000; border-radius: 20px;
        padding: 25px; margin-bottom: 20px; box-shadow: 8px 8px 0px #FF0000;
    }
    .price-box {
        background-color: #FFCC00; border: 4px solid #000; padding: 20px;
        border-radius: 15px; text-align: center; box-shadow: 6px 6px 0px #FF0000;
    }
    /* SVG Parça Efekti */
    path { cursor: pointer; transition: fill 0.3s; }
    path:hover { opacity: 0.8; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZİ ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    limit = min(len(fiyatlar), len(yillar))
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit]}).drop_duplicates()

# --- ARABA ŞEMASI PARÇALARI ---
parca_koordinatlari = {
    "Kaput": "M 110,60 L 190,60 L 185,140 L 115,140 Z",
    "Tavan": "M 115,160 L 185,160 L 180,260 L 120,260 Z",
    "Bagaj": "M 115,310 L 185,310 L 190,380 L 110,380 Z",
    "Sol Ön Çamur.": "M 70,70 L 105,70 L 110,135 L 75,135 Z",
    "Sağ Ön Çamur.": "M 195,70 L 230,70 L 225,135 L 190,135 Z",
    "Sol Ön Kapı": "M 75,145 L 112,145 L 118,215 L 80,215 Z",
    "Sağ Ön Kapı": "M 188,145 L 225,145 L 220,215 L 182,215 Z",
    "Sol Arka Kapı": "M 80,225 L 118,225 L 122,295 L 85,295 Z",
    "Sağ Arka Kapı": "M 182,225 L 220,225 L 215,295 L 178,295 Z",
    "Sol Arka Çamur.": "M 75,305 L 112,305 L 105,385 L 70,385 Z",
    "Sağ Arka Çamur.": "M 188,305 L 225,305 L 230,385 L 195,385 Z"
}

if 'ekspertiz' not in st.session_state:
    st.session_state.ekspertiz = {k: "Orijinal" for k in parca_koordinatlari.keys()}

# --- ANA EKRAN ---
st.markdown("<h1 style='text-align: center; color: #000;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    raw_input = st.text_area("📋 İlan Verilerini Yapıştır", height=150)
    if st.button("🚀 PİYASAYI ÇÖZ"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
else:
    col_input, col_car = st.columns([0.4, 0.6])

    with col_input:
        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
        v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        v_hasar = st.number_input("TRAMER (TL)", value=0)
        
        st.divider()
        st.write("🔧 **İşaretleme Modu**")
        mod = st.radio("Seçilen Parçayı Yap:", ["Boyalı (Sarı)", "Değişen (Kırmızı)", "Orijinal (Gri)"], horizontal=True)
        
        target_part = st.selectbox("Boyanacak Parçayı Seçin", list(parca_koordinatlari.keys()))
        if st.button("Parçayı İşaretle"):
            st.session_state.ekspertiz[target_part] = mod
        st.markdown("</div>", unsafe_allow_html=True)

    with col_car:
        # GERÇEKÇİ SVG ARABA ÇİZİMİ
        svg_code = '<svg viewBox="0 0 300 450" style="width:100%; max-width:400px; display:block; margin:auto;" xmlns="http://w3.org">'
        # Araba Silüeti (Gövde)
        svg_code += '<rect x="60" y="40" width="180" height="360" rx="50" fill="#f0f0f0" stroke="#000" stroke-width="2"/>'
        
        boya_count = 0
        degisen_count = 0

        for parca, path in parca_koordinatlari.items():
            durum = st.session_state.ekspertiz.get(parca, "Orijinal")
            renk = "#d1d1d1" # Orijinal Gri
            if "Boyalı" in durum:
                renk = "#FFCC00"; boya_count += 1
            elif "Değişen" in durum:
                renk = "#FF0000"; degisen_count += 1
            
            svg_code += f'<path d="{path}" fill="{renk}" stroke="#000" stroke-width="1.5" />'
        
        svg_code += '</svg>'
        st.markdown(svg_code, unsafe_allow_html=True)

    # --- HESAPLAMA ---
    df = st.session_state.data
    z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
    baz = np.poly1d(z)(v_yil)
    kesinti = (v_hasar * 0.2) + (boya_count * 15000) + (degisen_count * 35000)
    final_price = baz + (60000 if v_vites == "Otomatik" else 0) - kesinti

    st.markdown(f"""
        <div class='price-box'>
            <p style='color:#FF0000; font-weight:800; margin:0;'>HESAPLANAN DEĞER</p>
            <h1 style='color:#000; font-size:4rem; margin:0;'>{max(0, final_price):,.0f} TL</h1>
            <p style='color:#555;'>{boya_count} Boya | {degisen_count} Değişen</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        del st.session_state.ekspertiz
        st.rerun()
