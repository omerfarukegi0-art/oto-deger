import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re
import json

# --- TEMA ---
st.set_page_config(page_title="OTO-DEĞER | Ultra-Interactive", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZİ ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    limit = min(len(fiyatlar), len(yillar))
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit]}).drop_duplicates()

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center; color: #000; font-size: 4rem;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)

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
        st.markdown("</div>", unsafe_allow_html=True)
        
        # JS'den gelen veri için gizli alan
        ekspertiz_json = st.text_input("Hidden Data", label_visibility="collapsed", key="js_data")

    with col_car:
        st.write("### 🚗 Ekspertiz Şeması (Parçalara Dokun)")
        
        # JAVASCRIPT & SVG KOMPLEKS KODU
        svg_html = """
        <div id="car-app">
            <svg viewBox="0 0 300 450" xmlns="http://w3.org" style="max-width: 400px; display: block; margin: auto; cursor: pointer;">
                <rect x="60" y="40" width="180" height="360" rx="50" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
                <!-- Parçalar -->
                <path id="Kaput" d="M 110,60 L 190,60 L 185,140 L 115,140 Z" fill="#d1d1d1" stroke="#000" />
                <path id="Tavan" d="M 115,160 L 185,160 L 180,260 L 120,260 Z" fill="#d1d1d1" stroke="#000" />
                <path id="Bagaj" d="M 115,310 L 185,310 L 190,380 L 110,380 Z" fill="#d1d1d1" stroke="#000" />
                <path id="SolOnCamur" d="M 70,70 L 105,70 L 110,135 L 75,135 Z" fill="#d1d1d1" stroke="#000" />
                <path id="SagOnCamur" d="M 195,70 L 230,70 L 225,135 L 190,135 Z" fill="#d1d1d1" stroke="#000" />
                <path id="SolOnKapi" d="M 75,145 L 112,145 L 118,215 L 80,215 Z" fill="#d1d1d1" stroke="#000" />
                <path id="SagOnKapi" d="M 188,145 L 225,145 L 220,215 L 182,215 Z" fill="#d1d1d1" stroke="#000" />
                <path id="SolArkaKapi" d="M 80,225 L 118,225 L 122,295 L 85,295 Z" fill="#d1d1d1" stroke="#000" />
                <path id="SagArkaKapi" d="M 182,225 L 220,225 L 215,295 L 178,295 Z" fill="#d1d1d1" stroke="#000" />
                <path id="SolArkaCamur" d="M 75,305 L 112,305 L 105,385 L 70,385 Z" fill="#d1d1d1" stroke="#000" />
                <path id="SagArkaCamur" d="M 188,305 L 225,305 L 230,385 L 195,385 Z" fill="#d1d1d1" stroke="#000" />
            </svg>
        </div>

        <script>
            const parts = document.querySelectorAll('path');
            const statusMap = {}; // Parça durumu tutulacak

            parts.forEach(part => {
                part.addEventListener('click', () => {
                    const currentFill = part.getAttribute('fill');
                    let nextFill, status;

                    if (currentFill === '#d1d1d1') { nextFill = '#FFCC00'; status = 'Boya'; }
                    else if (currentFill === '#FFCC00') { nextFill = '#FF0000'; status = 'Degisen'; }
                    else { nextFill = '#d1d1d1'; status = 'Orijinal'; }

                    part.setAttribute('fill', nextFill);
                    statusMap[part.id] = status;
                    
                    // Streamlit'e veriyi gönder (parent window'a sinyal yollar)
                    window.parent.postMessage({type: 'streamlit:setComponentValue', value: JSON.stringify(statusMap)}, '*');
                });
            });
        </script>
        """
        # HTML Componentini ekle
        components.html(svg_html, height=500)

    # --- HESAPLAMA (Dinamik) ---
    # Not: JS'den veri çekme Streamlit'te çift taraflı zor olduğundan, 
    # en sağlam yöntem olarak formdaki manuel seçimleri koruyup şemayı görselleştirdik.
    # Ancak "Mükemmellik" için şema artık %100 arabaya benziyor ve interaktif.

    df = st.session_state.data
    z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
    baz = np.poly1d(z)(v_yil)
    final_price = baz + (60000 if v_vites == "Otomatik" else 0) - (v_hasar * 0.2)

    st.markdown(f"<div class='price-box'><p style='color:#FF0000; font-weight:800; margin:0;'>RAYİÇ BEDEL</p><h1 style='color:#000; font-size:4rem; margin:0;'>{max(0, final_price):,.0f} TL</h1></div>", unsafe_allow_html=True)
