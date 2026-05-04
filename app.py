import streamlit as st
import pandas as pd
import numpy as np
import re
import streamlit.components.v1 as components

# --- TEMA VE TASARIM ---
st.set_page_config(page_title="OTO-DEĞER | Ekspertiz", layout="wide")

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
        st.info("💡 Şemada parçaların üzerine tıklayarak durumlarını değiştirebilirsin.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_car:
        # SAHİBİNDEN STYLE REALISTIC SVG
        svg_html = """
        <div style="text-align:center;">
            <svg viewBox="0 0 300 500" width="380" xmlns="http://w3.org" style="cursor:pointer; user-select:none;">
                <!-- Ana Gövde Silüeti -->
                <path d="M 85,40 Q 150,15 215,40 L 225,100 L 245,250 L 225,400 L 215,460 Q 150,485 85,460 L 75,400 L 55,250 L 75,100 Z" fill="#f0f0f0" stroke="#ccc" stroke-width="1"/>
                
                <!-- Kaput (Aerodinamik Hatlar) -->
                <path id="Kaput" d="M 100,55 Q 150,45 200,55 L 205,145 Q 150,155 95,145 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.5" />
                
                <!-- Ön Cam / Panel -->
                <path d="M 105,155 L 195,155 L 200,175 L 100,175 Z" fill="#333" opacity="0.1"/>

                <!-- Tavan -->
                <path id="Tavan" d="M 110,185 L 190,185 Q 195,270 190,300 L 110,300 Q 105,270 110,185" fill="#d1d1d1" stroke="#333" stroke-width="1.5" />
                
                <!-- Bagaj -->
                <path id="Bagaj" d="M 105,365 L 195,365 Q 210,450 150,460 Q 90,450 105,365" fill="#d1d1d1" stroke="#333" stroke-width="1.5" />
                
                <!-- Sol Ön Çamurluk -->
                <path id="SolOnCamur" d="M 60,50 Q 80,45 90,55 L 100,145 L 65,150 Q 55,100 60,50" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                <!-- Sağ Ön Çamurluk -->
                <path id="SagOnCamur" d="M 240,50 Q 220,45 210,55 L 200,145 L 235,150 Q 245,100 240,50" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                
                <!-- Sol Ön Kapı -->
                <path id="SolOnKapi" d="M 68,160 L 105,160 L 108,245 L 70,245 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                <!-- Sağ Ön Kapı -->
                <path id="SagOnKapi" d="M 232,160 L 195,160 L 192,245 L 230,245 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                
                <!-- Sol Arka Kapı -->
                <path id="SolArkaKapi" d="M 70,250 L 108,250 L 112,325 L 72,325 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                <!-- Sağ Arka Kapı -->
                <path id="SagArkaKapi" d="M 230,250 L 192,250 L 188,325 L 228,325 Z" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                
                <!-- Sol Arka Çamurluk -->
                <path id="SolArkaCamur" d="M 72,335 L 100,335 L 100,450 Q 60,440 68,335" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />
                <!-- Sağ Arka Çamurluk -->
                <path id="SagArkaCamur" d="M 228,335 L 200,335 L 200,450 Q 240,440 232,335" fill="#d1d1d1" stroke="#333" stroke-width="1.2" />

                <!-- Aynalar (Görsel Detay) -->
                <rect x="45" y="150" width="15" height="5" rx="2" fill="#ccc"/>
                <rect x="240" y="150" width="15" height="5" rx="2" fill="#ccc"/>
            </svg>
            <div style="margin-top:15px; font-family:sans-serif; font-weight:bold;">
                <span style="color:#d1d1d1;">⚪ Orijinal</span> | 
                <span style="color:#FFCC00;">🟡 Boyalı</span> | 
                <span style="color:#FF0000;">🔴 Değişen</span>
            </div>
        </div>

        <script>
            const paths = document.querySelectorAll('path[id]');
            paths.forEach(p => {
                p.addEventListener('click', function() {
                    const colors = {
                        '#d1d1d1': '#FFCC00', 
                        '#FFCC00': '#FF0000', 
                        '#FF0000': '#d1d1d1'
                    };
                    const currentColor = this.getAttribute('fill');
                    this.setAttribute('fill', colors[currentColor] || '#d1d1d1');
                });
            });
        </script>
        """
        components.html(svg_html, height=600)

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
