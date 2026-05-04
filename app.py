import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bİ'EDERİ | Değerini Öğren", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. ANA ARKA PLAN */
    .stApp {
        background-color: #000000 !important;
        background-image: radial-gradient(circle at 50% 20%, #1a1a2e 0%, #000000 70%) !important;
    }

    /* 2. SİYAH KUTUCUKLARI SİLEN AGRESİF CSS */
    /* Tüm widget katmanlarını (div, span, button) şeffaf yapmaya zorlar */
    [data-testid="stNumberInput"] div, 
    [data-testid="stSelectbox"] div, 
    [data-testid="stMultiSelect"] div,
    [data-baseweb="input"], 
    [data-baseweb="select"],
    [data-baseweb="base-input"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* 3. GERÇEK GİRİŞ ALANLARINI YENİDEN TASARLA */
    /* Sadece yazı yazılan alanı koyu ve neon çizgili yap */
    input, 
    div[role="combobox"], 
    [data-baseweb="select"] > div {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #333 !important;
        border-bottom: 2px solid #FFCC00 !important; /* Altın sarısı neon çizgi */
        border-radius: 12px !important;
        padding: 10px !important;
        font-weight: 800 !important;
    }

    /* Çoklu seçim kutularının içindeki "etiketleri" (tag) düzenle */
    [data-testid="stMultiSelect"] span {
        background-color: #FF0000 !important;
        color: white !important;
    }

    /* 4. KART VE BAŞLIKLAR */
    .luxury-card {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 30px !important;
        padding: 40px !important;
        margin-bottom: 30px !important;
        backdrop-filter: blur(15px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        border-left: 6px solid #FF0000 !important;
    }

    h1, h2, h3, p, label {
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* 5. FİYAT VE BUTON */
    .price-box {
        background: linear-gradient(135deg, #FFCC00 0%, #FFAA00 100%) !important;
        padding: 40px !important;
        border-radius: 30px !important;
        text-align: center !important;
        box-shadow: 0 0 30px rgba(255, 204, 0, 0.3);
    }

    .stButton>button {
        background: linear-gradient(90deg, #FF0000 0%, #B20000 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 20px !important;
        height: 4em !important;
        text-transform: uppercase !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ANALİZ MOTORU ---
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
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]}).drop_duplicates()

# --- HEADER ---
st.markdown("<br><h1 style='text-align: center; font-size: 5rem;'>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FFCC00; font-weight: 800; letter-spacing: 5px; margin-top:-25px;'>GERÇEK DEĞERİNİ ÖĞRENİN</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; color:#FFF;'>📊 Verileri Buraya Aktarın</h3>", unsafe_allow_html=True)
    raw_input = st.text_area("", height=200, placeholder="İlanları kopyalayıp yapıştırın...")
    if st.button("ANALİZİ BAŞLAT"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- FORM ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("perfection_form"):
        st.markdown("<h3 style='margin-top:0; color:#FF0000;'>📋 Araç Özellikleri</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("MEVCUT KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0, step=1000)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yan Kapılar", "Çamurluklar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERİNİ ŞİMDİ ÖĞREN")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        katsayi = 4.2 if v_yil > 2021 else 3.5
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (65000 if v_vites == "Otomatik" else -15000) - (v_hasar * 0.18 + len(v_boya)*9000 + len(v_degisen)*22000)

        # --- SONUÇ ---
        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:800; letter-spacing:2px; opacity:0.7;'>TAHMİNİ SATIŞ FİYATI</p>
                <h1 style='color:#000; font-size:4rem; font-weight:900;'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
