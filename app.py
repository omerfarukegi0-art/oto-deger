import streamlit as st
import pandas as pd
import numpy as np
import re

# --- TERTEMİZ SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Değerini Öğren", layout="centered")

# --- KESİN ÇÖZÜM CSS (Siyahlıkları ve Görünmezliği Bitirir) ---
st.markdown("""
    <style>
    /* 1. ANA ARKA PLAN */
    .stApp { background-color: #000000 !important; }

    /* 2. TÜM YAZILARI BEYAZA ZORLA (Model Yılı vb. için) */
    h1, h2, h3, p, label, span, div { color: #FFFFFF !important; }
    
    /* 3. KUTUCUKLARDAKİ SİYAHLIKLARI TEMİZLE */
    /* Giriş kutularını gri dolgu ve altın çerçeve yap */
    input, div[data-baseweb="select"] > div {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #d4af37 !important;
        border-radius: 10px !important;
    }

    /* MultiSelect (Boya/Değişen) baloncuklarını kırmızı yap */
    div[data-baseweb="tag"] {
        background-color: #FF0000 !important;
        color: white !important;
    }

    /* Sayı girişindeki artı-eksi butonlarını gizle */
    button[step] { display: none !important; }

    /* 4. LÜKS KART */
    .luxury-card {
        background-color: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 20px !important;
        padding: 30px !important;
        margin-bottom: 20px !important;
        border-left: 5px solid #FF0000 !important;
    }

    /* 5. FİYAT PANELİ */
    .price-box {
        background-color: #FFCC00 !important;
        padding: 30px !important;
        border-radius: 20px !important;
        text-align: center !important;
    }
    .price-val { color: #000000 !important; font-size: 3.5rem !important; font-weight: 800 !important; }

    /* 6. KIRMIZI BUTON */
    .stButton>button {
        background-color: #FF0000 !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        height: 3.5em !important;
        width: 100% !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZİ ---
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
st.markdown("<h1 style='text-align: center;'>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #d4af37 !important;'>Gerçek Değerini Keşfedin</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini Yapıştır", height=200)
    if st.button("ANALİZİ BAŞLAT"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("perfection_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("📅 MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("🛣️ MEVCUT KİLOMETRE", value=50000)
            v_vites = st.radio("🕹️ ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("💸 TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", ["Kaput", "Bagaj", "Kapı"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERİNİ ÖĞREN")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * 4.0 + (60000 if v_vites == "Otomatik" else -20000) - (v_hasar * 0.15 + len(v_boya)*9000 + len(v_degisen)*25000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:700; opacity:0.7;'>TAHMİNİ RAYİÇ BEDEL</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
