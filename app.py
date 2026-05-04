import streamlit as st
import pandas as pd
import numpy as np
import re

# --- TEMA AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | İnteraktif Ekspertiz", layout="wide")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #FFFFFF; }
    
    /* Şema Butonları Tasarımı */
    .stButton>button {
        border-radius: 8px;
        border: 2px solid #000;
        font-weight: 800;
        font-size: 0.7rem;
        height: 45px;
        width: 100%;
        transition: 0.2s;
    }
    .luxury-card {
        background: #FFFFFF; border: 3px solid #000; border-radius: 20px;
        padding: 20px; box-shadow: 6px 6px 0px #FF0000;
    }
    .price-box {
        background-color: #FFCC00; border: 4px solid #000;
        border-radius: 15px; text-align: center; box-shadow: 6px 6px 0px #FF0000;
        padding: 20px; margin-top: 20px;
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
st.markdown("<h1 style='text-align: center; color: #000;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    raw_input = st.text_area("📋 İlan Verilerini Yapıştır", height=150)
    if st.button("🚀 PİYASAYI ANALİZ ET"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.session_state.ekspertiz = {} # Ekspertiz verisini başlat
            st.rerun()
else:
    # --- İNTERAKTİF ŞEMA ALANI ---
    df = st.session_state.data
    
    col_input, col_car = st.columns([0.3, 0.7])

    with col_input:
        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        v_yil = st.selectbox("MODEL YILI", sorted(df["Yıl"].unique(), reverse=True))
        v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        v_hasar = st.number_input("TRAMER (TL)", value=0)
        st.write("---")
        st.write("🎨 **Renk Seçimi**")
        mod = st.radio("İşaretleme Modu", ["Boyalı (Sarı)", "Değişen (Kırmızı)", "Orijinal (Gri)"], horizontal=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_car:
        st.write("### 🚗 Araç Şeması (İşaretlemek için parçaya tıkla)")
        
        # Parçaları araba formunda dizelim (Kuş bakışı simülasyonu)
        # ÖN KISIM
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: 
            if st.button("Sol Ön Çam."): st.session_state.ekspertiz["Sol Ön Çamur."] = mod
        with c2: 
            if st.button("KAPUT"): st.session_state.ekspertiz["Kaput"] = mod
        with c3: 
            if st.button("Sağ Ön Çam."): st.session_state.ekspertiz["Sağ Ön Çamur."] = mod

        # ORTA KISIM
        c4, c5, c6 = st.columns([1, 2, 1])
        with c4: 
            if st.button("Sol Ön Kapı"): st.session_state.ekspertiz["Sol Ön Kapı"] = mod
            if st.button("Sol Arka Kapı"): st.session_state.ekspertiz["Sol Arka Kapı"] = mod
        with c5: 
            if st.button("TAVAN"): st.session_state.ekspertiz["Tavan"] = mod
        with c6: 
            if st.button("Sağ Ön Kapı"): st.session_state.ekspertiz["Sağ Ön Kapı"] = mod
            if st.button("Sağ Arka Kapı"): st.session_state.ekspertiz["Sağ Arka Kapı"] = mod

        # ARKA KISIM
        c7, c8, c9 = st.columns([1, 2, 1])
        with c7: 
            if st.button("Sol Arka Çam."): st.session_state.ekspertiz["Sol Arka Çamur."] = mod
        with c8: 
            if st.button("BAGAJ"): st.session_state.ekspertiz["Bagaj Kapağı"] = mod
        with c9: 
            if st.button("Sağ Arka Çam."): st.session_state.ekspertiz["Sağ Arka Çamur."] = mod

    # --- HESAPLAMA VE GÖSTERİM ---
    boya_count = sum(1 for v in st.session_state.ekspertiz.values() if "Boyalı" in v)
    degisen_count = sum(1 for v in st.session_state.ekspertiz.values() if "Değişen" in v)
    
    z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
    baz = np.poly1d(z)(v_yil)
    
    # Hesaplama (Boya başına 12k, Değişen başına 25k, Tramer %20)
    kesinti = (v_hasar * 0.2) + (boya_count * 12000) + (degisen_count * 25000)
    final_price = baz + (60000 if v_vites == "Otomatik" else 0) - kesinti

    st.markdown(f"""
        <div class='price-box'>
            <p style='color:#FF0000; font-weight:800; margin:0;'>RAYİÇ BEDEL</p>
            <h1 style='color:#000; font-size:4rem; margin:0;'>{max(0, final_price):,.0f} TL</h1>
            <p style='color:#555; font-size:0.8rem;'>{boya_count} Boya | {degisen_count} Değişen İşaretlendi</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA VE BAŞTAN BAŞLA"):
        del st.session_state.data
        del st.session_state.ekspertiz
        st.rerun()
