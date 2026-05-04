import streamlit as st
import pandas as pd
import numpy as np
import re
import streamlit.components.v1 as components

# --- TEMA VE TASARIM ---
st.set_page_config(page_title="OTO-DEĞER | Professional", layout="wide")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #FFFFFF; }
    .luxury-card {
        background: #FFFFFF; border: 1px solid #e0e0e0; border-radius: 20px;
        padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .price-box {
        background-color: #FFCC00; border: 3px solid #000; padding: 20px;
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
st.markdown("<h1 style='text-align: center; color: #000; font-size: 3.5rem; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Verilerini Yapıştır", height=150)
    if st.button("🚀 PİYASAYI ANALİZ ET"):
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
        v_hasar = st.number_input("TRAMER (TL)", value=0, step=1000)
        st.divider()
        st.write("🔧 **Ekspertiz Talimatı:**")
        st.caption("Sağdaki şemada parçalara tıklayın. Döngü: Orijinal -> Boyalı -> Değişen.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_car:
        # ARABAM.COM STYLE PROFESYONEL ŞEMA (SVG)
        svg_html = """
        <div style="text-align:center;">
            <svg viewBox="0 0 300 550" width="380" xmlns="http://w3.org" style="cursor:pointer; user-select:none;">
                <!-- Ön Tampon -->
                <path id="OnTampon" d="M 100,20 Q 150,5 200,20 L 205,40 Q 150,30 95,40 Z" fill="#EBEBEB" stroke="#666" stroke-width="1" />
                
                <!-- Motor Kaputu -->
                <path id="MotorKaputu" d="M 95,50 L 205,50 L 195,155 L 105,155 Z" fill="#EBEBEB" stroke="#666" stroke-width="1.5" />
                
                <!-- Tavan -->
                <path id="Tavan" d="M 110,195 L 190,195 L 185,325 L 115,325 Z" fill="#EBEBEB" stroke="#666" stroke-width="1.5" />
                
                <!-- Arka Kaput (Bagaj) -->
                <path id="ArkaKaput" d="M 110,400 L 190,400 L 200,480 Q 150,500 100,480 Z" fill="#EBEBEB" stroke="#666" stroke-width="1.5" />

                <!-- Sol Ön Çamurluk -->
                <path id="SolOnCamur" d="M 60,50 Q 80,45 85,55 L 95,160 L 60,165 Q 50,100 60,50" fill="#EBEBEB" stroke="#666" stroke-width="1.2" />
                <!-- Sağ Ön Çamurluk -->
                <path id="SagOnCamur" d="M 240,50 Q 220,45 215,55 L 205,160 L 240,165 Q 250,100 240,50" fill="#EBEBEB" stroke="#666" stroke-width="1.2" />

                <!-- Sol Ön Kapı -->
                <path id="SolOnKapi" d="M 65,175 L 105,175 L 108,275 L 68,275 Z" fill="#EBEBEB" stroke="#666" stroke-width="1.2" />
                <!-- Sağ Ön Kapı -->
                <path id="SagOnKapi" d="M 235,175 L 195,175 L 192,275 L 232,275 Z" fill="#EBEBEB" stroke="#666" stroke-width="1.2" />

                <!-- Sol Arka Kapı -->
                <path id="SolArkaKapi" d="M 68,285 L 108,285 L 112,385 L 72,385 Z" fill="#EBEBEB" stroke="#666" stroke-width="1.2" />
                <!-- Sağ Arka Kapı -->
                <path id="SagArkaKapi" d="M 232,285 L 192,285 L 188,385 L 228,385 Z" fill="#EBEBEB" stroke="#666" stroke-width="1.2" />

                <!-- Sol Arka Çamurluk -->
                <path id="SolArkaCamur" d="M 75,395 L 100,395 L 95,490 Q 60,480 65,400" fill="#EBEBEB" stroke="#666" stroke-width="1.2" />
                <!-- Sağ Arka Çamurluk -->
                <path id="SagArkaCamur" d="M 225,395 L 200,395 L 205,490 Q 240,480 235,400" fill="#EBEBEB" stroke="#666" stroke-width="1.2" />
                
                <!-- Arka Tampon -->
                <path id="ArkaTampon" d="M 100,500 Q 150,520 200,500 L 205,520 Q 150,540 95,520 Z" fill="#EBEBEB" stroke="#666" stroke-width="1" />
            </svg>
            <div style="margin-top:15px; font-family:sans-serif; font-size:14px;">
                <span style="color:#666;">⚪ Orijinal</span> &nbsp; 
                <span style="color:#FFCC00;">🟡 Boyalı</span> &nbsp; 
                <span style="color:#FF0000;">🔴 Değişmiş</span>
            </div>
        </div>

        <script>
            const paths = document.querySelectorAll('path');
            paths.forEach(p => {
                p.addEventListener('click', function() {
                    const colors = {
                        '#EBEBEB': '#FFCC00', // Gri -> Sarı
                        '#FFCC00': '#FF0000', // Sarı -> Kırmızı
                        '#FF0000': '#EBEBEB'  // Kırmızı -> Gri
                    };
                    const current = this.getAttribute('fill').toUpperCase();
                    this.setAttribute('fill', colors[current] || '#EBEBEB');
                });
            });
        </script>
        """
        components.html(svg_html, height=600)

    # --- HESAPLAMA VE SONUÇ ---
    df = st.session_state.data
    z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
    baz = np.poly1d(z)(v_yil)
    
    # Gerçekçi Rayiç Bedel Hesabı
    final_price = baz + (60000 if v_vites == "Otomatik" else 0) - (v_hasar * 0.18)

    st.markdown(f"""
        <div class='price-box'>
            <h1 style='color:#000; font-size:4rem; margin:0;'>{max(0, final_price):,.0f} TL</h1>
            <p style='color:#FF0000; font-weight:800; margin:0;'>HESAPLANAN RAYİÇ BEDEL</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
