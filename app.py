import streamlit as st
import pandas as pd
import numpy as np
import re

# --- PRESTİJ AYARLARI ---
st.set_page_config(page_title="Bİ'EDERİ | Elite", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* 1. ARKA PLAN */
    .stApp {
        background-color: #000000 !important;
        background-image: radial-gradient(circle at 50% 10%, #161b22 0%, #000000 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* 2. BALONCUKLARI SİLEN VE KUTULARI GİZLEYEN RENK AYARI */
    /* Giriş alanlarını kart rengiyle (#161b22) birebir eşitliyoruz */
    div[data-baseweb="input"], 
    div[data-baseweb="select"], 
    div[data-baseweb="base-input"],
    .stNumberInput div, .stSelectbox div, .stMultiSelect div {
        background-color: #161b22 !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Yazı yazılan yerleri şıklaştır */
    input, div[role="combobox"], [data-baseweb="select"] > div {
        background-color: #161b22 !important; 
        color: #FFFFFF !important;
        border: 1px solid #30363d !important;
        border-bottom: 2px solid #FFCC00 !important; /* Altın sarısı ince hat */
        border-radius: 12px !important;
        padding: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* 3. LÜKS KART: Boyutlar Daraltıldı */
    .luxury-card {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 25px !important;
        padding: 30px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.5);
        border-left: 4px solid #FF0000 !important;
    }

    /* 4. YAZI BOYUTLARI: Daha Zarif */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -1px !important;
        color: #FFFFFF !important;
        font-size: 3.5rem !important; /* Küçültüldü */
        margin-bottom: 10px !important;
    }
    
    .tagline {
        color: #888 !important;
        letter-spacing: 5px !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        margin-top: -15px;
        margin-bottom: 20px;
    }

    /* 5. FİYAT EKRANI: Optimize Edildi */
    .price-box {
        background: linear-gradient(135deg, #FFCC00 0%, #FF9900 100%) !important;
        padding: 35px 20px !important;
        border-radius: 25px !important;
        text-align: center !important;
        margin: 25px 0 !important;
    }
    
    .price-val { 
        color: #000000 !important; 
        font-size: 3.8rem !important; /* Küçültüldü */
        font-weight: 800 !important; 
        letter-spacing: -2px !important;
        line-height: 1;
    }

    /* 6. BUTON: Daha Profesyonel */
    .stButton>button {
        background: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        border: none !important;
        text-transform: uppercase !important;
    }

    label { color: #888 !important; font-weight: 600 !important; font-size: 0.8rem !important; }
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
st.markdown("<br><h1 style='text-align: center;'>Bİ'EDERİ</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline' style='text-align: center;'>Gerçek Değerini Keşfedin</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Verilerini Yapıştırın", height=150)
    if st.button("ANALİZİ BAŞLAT"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("elite_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("MEVCUT KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0, step=1000)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERİNİ ÖĞREN")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        katsayi = 4.2 if v_yil > 2022 else 3.5
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (65000 if v_vites == "Otomatik" else -20000) - (v_hasar * 0.15 + len(v_boya)*9000 + len(v_degisen)*25000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:700; letter-spacing:2px; opacity:0.6; font-size:0.8rem;'>TAHMİNİ PAZAR DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ SIFIRLA"):
        del st.session_state.data
        st.rerun()
