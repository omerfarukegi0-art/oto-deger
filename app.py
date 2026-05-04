import streamlit as st
import pandas as pd
import numpy as np
import re

# --- RENK VE TEMA AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | Sport", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* Arka Plan: Yumuşak Gradyan Geçişi */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f4f4f4 100%) !important;
    }

    /* Tüm Yazılar Siyah ve Net */
    h1, h2, h3, p, label, span, .stMarkdown, .stSelectbox, .stNumberInput, .stRadio {
        color: #000000 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Lüks Kartlar: Kırmızı Çizgili Detay */
    .luxury-card {
        background: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 20px !important;
        padding: 30px !important;
        margin-bottom: 25px !important;
        box-shadow: 8px 8px 0px #FF0000 !important; /* Kırmızı Sert Gölge */
    }

    /* Fiyat Paneli: Sarı & Siyah Zirvesi */
    .price-box {
        background-color: #FFCC00 !important;
        padding: 30px !important;
        border-radius: 20px !important;
        border: 4px solid #000000 !important;
        text-align: center !important;
        margin: 25px 0 !important;
        box-shadow: 10px 10px 0px #000000 !important;
    }
    .price-label { 
        color: #FF0000 !important; 
        font-weight: 900 !important; 
        letter-spacing: 3px !important; 
        text-transform: uppercase;
        margin-bottom: 5px !important;
    }
    .price-val { 
        color: #000000 !important; 
        font-size: 5rem !important; 
        font-weight: 900 !important; 
        line-height: 1 !important;
    }

    /* Kırmızı Ana Buton */
    .stButton>button {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        border: 3px solid #000000 !important;
        height: 3.5em !important;
        text-transform: uppercase !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        transform: translate(-2px, -2px) !important;
        box-shadow: 5px 5px 0px #000000 !important;
    }

    /* Input Odak Renkleri */
    .stSelectbox:focus, .stNumberInput:focus {
        border-color: #FF0000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ İŞLEME ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    kms = []
    km_adaylari = re.findall(r"\b(\d{1,3}[\.,]\d{3})\b", metin)
    for k in km_adaylari:
        sayi = int(k.replace(".", "").replace(",", ""))
        if 500 < sayi < 600000 and sayi not in fiyatlar:
            kms.append(sayi)
    
    limit = min(len(fiyatlar), len(yillar), len(kms))
    if limit == 0: return pd.DataFrame()
    df = pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]})
    return df.drop_duplicates()

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center; font-size: 5.5rem; font-weight: 900; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000 !important; font-weight: 900; font-size: 1.3rem; margin-top:-25px; letter-spacing: 2px;'>🏁 DİNAMİK ANALİZ & EKSPERTİZ</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📋 İlan Verilerini Yapıştır</h3>", unsafe_allow_html=True)
    raw_input = st.text_area("", height=200, placeholder="Sahibinden metnini buraya kopyalayın...")
    if st.button("🚀 PİYASAYI ÇÖZ"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- FORM ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("sport_form"):
        st.markdown("<h3 style='margin-top:0;'>🔍 Araç Durumu</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        submit = st.form_submit_button("💰 DEĞERİ HESAPLA")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        
        # Dinamik KM Katsayısı
        if len(yil_verisi) >= 2:
            katsayi, _ = np.polyfit(yil_verisi["KM"], yil_verisi["Fiyat"], 1)
            final_katsayi = abs(katsayi) if katsayi < 0 else 3.8
        else:
            final_katsayi = 4.2 if v_yil > 2021 else 3.2

        # Baz Fiyat (Piyasa Trendi)
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz_fiyat = np.poly1d(z)(v_yil)
        
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        km_bonusu = (km_ort - v_km) * final_katsayi
        
        final_price = (baz_fiyat * 1.05) + km_bonusu + (65000 if v_vites == "Otomatik" else -15000) - (v_hasar * 0.18 + len(v_boya)*8500 + len(v_degisen)*19000)

        # --- SONUÇ PANELİ ---
        st.markdown(f"""
            <div class='price-box'>
                <p class='price-label'>Güncel Rayiç Bedel</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ SIFIRLA"):
        del st.session_state.data
        st.rerun()
