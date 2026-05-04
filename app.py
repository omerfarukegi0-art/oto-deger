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
        # GERÇEKÇİ ARABA SİLUETİ (SVG)
        svg_html = """
        <div style="text-align:center;">
            <svg viewBox="0 0 300 500" width="380" xmlns="http://w3.org" style="cursor:pointer; user-select:none;">
                <!-- Araba Dış Hat (Gövde) -->
                <path d="M 80,50 Q 150,20 220,50 L 235,120 L 245,250 L 235,380 L 220,450 Q 150,480 80,450 L 65,380 L 55,250 L 65,120 Z" fill="#f0f0f0" stroke="#ccc" stroke-width="2"/>
                
                <!-- Kaput -->
                <path id="Kaput" d="M 95,65 L 205,65 Q 200,140 195,150 L 105,150 Q 100,140 95,65" fill="#d1d1d1" stroke="#333" stroke-width="1.5" />
                <!-- Tavan -->
                <path id="Tavan" d="M 110,170 L 190,170 Q 185,280 180,290 L 120,290 Q 115,280 110,170" fill="#d1d1d1" stroke="#333" stroke-width="1.5" />
                <!-- Bagaj -->
                <path id="Bagaj" d="M 105,340 L 195,340 L 205,430 Q 150,450 95,430 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.5" />
                
                <!-- Sol Ön Çamurluk -->
                <path id="SolOnCamur" d="M 60,60 Q 85,55 90,65 L 100,150 L 65,155 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                <!-- Sağ Ön Çamurluk -->
                <path id="SagOnCamur" d="M 240,60 Q 215,55 210,65 L 200,150 L 235,155 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                
                <!-- Sol Ön Kapı -->
                <path id="SolOnKapi" d="M 65,165 L 105,165 L 112,245 L 70,245 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                <!-- Sağ Ön Kapı -->
                <path id="SagOnKapi" d="M 235,165 L 195,165 L 188,245 L 230,245 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                
                <!-- Sol Arka Kapı -->
                <path id="SolArkaKapi" d="M 70,255 L 112,255 L 118,330 L 75,330 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                <!-- Sağ Arka Kapı -->
                <path id="SagArkaKapi" d="M 230,255 L 188,255 L 182,330 L 225,330 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                
                <!-- Sol Arka Çamurluk -->
                <path id="SolArkaCamur" d="M 75,340 L 100,340 L 95,435 Q 60,420 65,345 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                <!-- Sağ Arka Çamurluk -->
                <path id="SagArkaCamur" d="M 225,340 L 200,340 L 205,435 Q 240,420 235,345 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
            </svg>
            <div style="margin-top:10px; font-family:sans-serif; font-weight:bold;">
                <span style="color:#888;">⚪ Orijinal</span> | 
                <span style="color:#FFCC00;">🟡 Boyalı</span> | 
                <span style="color:#FF0000;">🔴 Değişen</span>
            </div>
        </div>

        <script>
            const paths = document.querySelectorAll('path[id]');
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
        components.html(svg_html, height=580)

    # --- HESAPLAMA ---
    df = st.session_state.data
    z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
    baz = np.poly1d(z)(v_yil)
    final_price = baz + (60000 if v_vites == "Otomatik" else 0) - (v_hasar * 0.2)

    st.markdown(f"""
        <div class='price-box'>
            <h1 style='color:#000; font-size:4rem; margin:0;'>{max(0, final_price):,.0f} TL</h1>
            <p style='color:#FF0000; font-weight:800; margin:0;'>TAHMİNİ RAYİÇ BEDEL</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE VE BAŞTAN BAŞLA"):
        del st.session_state.data
        st.rerun()
