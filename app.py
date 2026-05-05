import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Trink Sat", layout="centered")

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #FFFFFF !important; font-family: sans-serif; font-weight: 800; text-align: center; font-size: 3.5rem !important; }
    .luxury-card {
        background-color: #161b22;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #30363d;
        border-left: 5px solid #FF0000;
        margin-bottom: 20px;
    }
    .trink-box { 
        background: linear-gradient(135deg, #FF0000 0%, #990000 100%); 
        padding: 2.5rem; 
        border-radius: 20px; 
        text-align: center; 
        margin: 20px 0; 
        border: 2px solid #FFF;
        box-shadow: 0 10px 30px rgba(255, 0, 0, 0.3);
    }
    .price-val { color: #FFFFFF; font-size: 3.8rem; font-weight: 900; margin: 0; }
    .stButton>button {
        background-color: #FF0000 !important; color: white !important;
        font-weight: 700 !important; width: 100%; height: 4em; border-radius: 12px; border: none; text-transform: uppercase;
    }
    label { color: #d4af37 !important; font-weight: 700; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZİ ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    kms = [int(k.replace(".", "").replace(",", "")) for k in re.findall(r"\b(\d{1,3}[\.,]\d{3})\b", metin) if int(k.replace(".", "").replace(",", "")) not in fiyatlar]
    limit = min(len(fiyatlar), len(yillar), len(kms))
    if limit == 0: return pd.DataFrame()
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]}).drop_duplicates()

parcalar = ["Kaput", "Tavan", "Bagaj Kapağı", "Sol Ön Çamur.", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamur.", "Sağ Ön Çamurluk", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamur."]

st.markdown("<h1>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>")

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 Piyasa İlanlarını Buraya Yapıştırın", height=200)
    if st.button("PİYASAYI ANALİZ ET"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("trink_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", parcalar)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", parcalar)
        submit = st.form_submit_button("TRİNK NAKİT FİYATI AL")

    if submit:
        df = st.session_state.data
        yil_daslar = df[df["Yıl"] == v_yil].copy()
        
        # --- TRİNK SAT HESAPLAMA ALGORİTMASI ---
        if not yil_daslar.empty:
            # İlanlardaki aşırı uç fiyatları eliyoruz (Filtreleme)
            p_low = yil_daslar["Fiyat"].quantile(0.15)
            p_high = yil_daslar["Fiyat"].quantile(0.85)
            filtered_df = yil_daslar[(yil_daslar["Fiyat"] > p_low) & (yil_daslar["Fiyat"] < p_high)]
            
            # KM düzeltmesi yapılmış baz fiyat
            base_rayic = filtered_df["Fiyat"].mean()
            km_farki = filtered_df["KM"].mean() - v_km
            adjusted_rayic = base_rayic + (km_farki * 4.5)
        else:
            z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
            adjusted_rayic = np.poly1d(z)(v_yil)

        # Ekspertiz Düşümleri
        boya_orani = sum([0.025 if p in ["Tavan", "Kaput"] else 0.015 for p in v_boya])
        degisen_orani = sum([0.05 if p in ["Tavan", "Kaput"] else 0.035 for p in v_degisen])
        eksper_kaybi = adjusted_rayic * (boya_orani + degisen_orani) + (v_hasar * 0.20)
        
        # Pazar Değeri
        pazar_degeri = adjusted_rayic - eksper_kaybi
        if v_vites == "Otomatik": pazar_degeri += 70000
        
        # TRİNK SAT MAKASI (Arabam.com'un yaptığı nakit alım kesintisi: %10)
        trink_fiyat = pazar_degeri * 0.90

        # --- SONUÇ ---
        st.markdown(f"""
            <div class='trink-box'>
                <p style='color:#FFF; font-weight:700; opacity:0.8; margin-bottom:10px;'>TRİNK NAKİT ALIM FİYATI</p>
                <h1 class='price-val'>{max(0, trink_fiyat):,.0f} TL</h1>
                <p style='color:#FFF; font-size:0.9rem; margin-top:10px;'>Piyasa Değeri: {max(0, pazar_degeri):,.0f} TL</p>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 YENİ SORGULAMA"):
        del st.session_state.data
        st.rerun()
