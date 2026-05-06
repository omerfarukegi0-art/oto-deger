import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Trink Sat", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #FFFFFF !important; font-family: sans-serif; font-weight: 800; text-align: center; font-size: 3.5rem !important; }
    .luxury-card {
        background-color: #161b22;
        padding: 2.5rem;
        border-radius: 25px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .trink-box { 
        background: linear-gradient(135deg, #FF0000 0%, #B20000 100%); 
        padding: 2.5rem; 
        border-radius: 25px; 
        text-align: center; 
        margin: 20px 0; 
        border: 2px solid #FFF;
    }
    .price-val { color: #FFFFFF; font-size: 3.8rem; font-weight: 900; margin: 0; }
    .stButton>button {
        background-color: #FF0000 !important; color: white !important;
        font-weight: 800 !important; width: 100%; height: 4em; border-radius: 15px; border: none; text-transform: uppercase;
    }
    label { color: #d4af37 !important; font-weight: 700; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    kms = [int(k.replace(".", "").replace(",", "")) for k in re.findall(r"\b(\d{1,3}[\.,]\d{3})\b", metin) if int(k.replace(".", "").replace(",", "")) not in fiyatlar]
    limit = min(len(fiyatlar), len(yillar), len(kms))
    if limit == 0: return pd.DataFrame()
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]}).drop_duplicates()

parcalar = ["Kaput", "Tavan", "Bagaj Kapağı", "Sol Ön Çamur.", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamur.", "Sağ Ön Çamur.", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamur."]

st.markdown("<h1>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>")

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Metnini Yapıştırın", height=200)
    if st.button("ANALİZİ BAŞLAT"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("trink_fix"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", parcalar)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", parcalar)
        submit = st.form_submit_button("TRİNK NAKİT TEKLİFİ AL")

    if submit:
        df = st.session_state.data
        yil_daslar = df[df["Yıl"] == v_yil].copy()
        
        if not yil_daslar.empty:
            # 1. BAZ FİYATI DÜZELTME: Artık en ucuzları değil, merkeze yakın alt dilimi alıyoruz (%35 kuantil)
            base_fiyat = yil_daslar["Fiyat"].quantile(0.35)
            
            # 2. KM DÜZELTMESİ (Daha yumuşak katsayı)
            km_ort = yil_daslar["KM"].mean()
            km_farki = km_ort - v_km
            km_etkisi = km_farki * 3.2 
            
            pazar_rayici = base_fiyat + km_etkisi
        else:
            z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
            pazar_rayici = np.poly1d(z)(v_yil)

        # 3. EKSPERTİZ DÜŞÜMLERİ (Piyasa standartlarına çekildi)
        boya_kaybi = len(v_boya) * 7500
        degisen_kaybi = len(v_degisen) * 18000
        tramer_kaybi = v_hasar * 0.15
        
        if v_vites == "Otomatik": pazar_rayici += 50000
        
        nihai_rayic = pazar_rayici - (boya_kaybi + degisen_kaybi + tramer_kaybi)
        
        # 4. TRİNK MAKASI: %10 yerine %6-7 seviyesine daraltıldı (Kurumsal kâr marjı normalleştirildi)
        trink_fiyat = nihai_rayic * 0.935 

        st.markdown(f"""
            <div class='trink-box'>
                <p style='color:#FFF; font-weight:700; opacity:0.8; margin-bottom:10px;'>TRİNK NAKİT TEKLİFİ</p>
                <h1 class='price-val'>{max(0, trink_fiyat):,.0f} TL</h1>
                <p style='color:#FFF; font-size:0.9rem; margin-top:10px;'>Piyasa Değeri: {max(0, nihai_rayic):,.0f} TL</p>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
