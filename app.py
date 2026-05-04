import streamlit as st
import pandas as pd
import numpy as np
import re
import streamlit.components.v1 as components

# --- TEMA VE TASARIM ---
st.set_page_config(page_title="OTO-DEĞER | Pro Ekspertiz", layout="wide")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
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

# --- VERİ ANALİZ MOTORU ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    limit = min(len(fiyatlar), len(yillar))
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit]}).drop_duplicates()

# --- ANA EKRAN ---
st.markdown("<h1 style='text-align: center; color: #000; font-size: 4rem;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Verilerini Yapıştır", height=150)
    if st.button("🚀 PİYASAYI ÇÖZ"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    col_input, col_car = st.columns([0.4, 0.6])

    with col_input:
        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
        v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        v_hasar = st.number_input("TRAMER (TL)", value=0)
        st.divider()
        st.info("💡 Sağdaki araç şemasında parçaların üzerine tıklayarak durumlarını değiştirebilirsin.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_car:
        # JAVASCRIPT DESTEKLİ GERÇEKÇİ ARABA ŞEMASI
        # Her parça gerçek araba formunda çizildi (SVG Path)
        svg_html = """
        <div style="text-align:center;">
            <svg viewBox="0 0 300 500" width="350" xmlns="http://w3.org" style="cursor:pointer; user-select:none;">
                <!-- Arka Plan Gövde -->
                <rect x="70" y="30" width="160" height="440" rx="50" fill="#f8f8f8" stroke="#ddd" stroke-width="2"/>
                
                <!-- Parçalar (İnteraktif) -->
                <path id="Kaput" d="M 100,60 L 200,60 L 195,140 L 105,140 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                <path id="Tavan" d="M 110,165 L 190,165 L 185,275 L 115,275 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                <path id="Bagaj" d="M 105,330 L 195,330 L 205,420 L 95,420 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                
                <path id="SolOnCamur" d="M 65,70 L 95,70 L 100,135 L 68,135 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                <path id="SagOnCamur" d="M 205,70 L 235,70 L 232,135 L 200,135 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                
                <path id="SolOnKapi" d="M 70,145 L 108,145 L 113,230 L 73,230 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                <path id="SagOnKapi" d="M 192,145 L 230,145 L 227,230 L 187,230 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                
                <path id="SolArkaKapi" d="M 73,240 L 113,240 L 118,320 L 78,320 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                <path id="SagArkaKapi" d="M 187,240 L 227,240 L 222,320 L 182,320 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                
                <path id="SolArkaCamur" d="M 68,330 L 100,330 L 95,420 L 65,420 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
                <path id="SagArkaCamur" d="M 200,330 L 232,330 L 235,420 L 205,420 Z" fill="#d1d1d1" stroke="#000" stroke-width="1.5" />
            </svg>
            <div style="margin-top:10px; font-family:sans-serif; font-weight:bold;">
                <span style="color:#888;">⚪ Orijinal</span> | 
                <span style="color:#FFCC00;">🟡 Boyalı</span> | 
                <span style="color:#FF0000;">🔴 Değişen</span>
            </div>
        </div>

        <script>
            const paths = document.querySelectorAll('path');
            paths.forEach(p => {
                p.addEventListener('click', function() {
                    const colors = {
                        '#d1d1d1': '#FFCC00', // Gri -> Sarı
                        '#FFCC00': '#FF0000', // Sarı -> Kırmızı
                        '#FF0000': '#d1d1d1'  // Kırmızı -> Gri
                    };
                    const currentColor = this.getAttribute('fill');
                    this.setAttribute('fill', colors[currentColor] || '#d1d1d1');
                });
            });
        </script>
        """
        components.html(svg_html, height=550)

    # --- HESAPLAMA ---
    df = st.session_state.data
    z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
    baz = np.poly1d(z)(v_yil)
    
    # Not: JS'deki renk değişimi anlık olarak fiyata yansıması için Streamlit'in
    # özel bir component yapısı gerekir. Şimdilik bu şık görseli manuel seçimle 
    # birleştirip fiyata yansıtalım.
    
    final_price = baz + (60000 if v_vites == "Otomatik" else 0) - (v_hasar * 0.2)

    st.markdown(f"""
        <div class='price-box'>
            <h1 style='color:#000; font-size:4rem; margin:0;'>{max(0, final_price):,.0f} TL</h1>
            <p style='color:#FF0000; font-weight:800; margin:0;'>TAHMİNİ RAYİÇ DEĞER</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA VE BAŞTAN BAŞLA"):
        del st.session_state.data
        st.rerun()
