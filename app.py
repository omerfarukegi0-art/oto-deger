import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bİ'EDERİ | Değerini Öğren", layout="centered")

# --- HATA VERMEYEN TERTEMİZ CSS ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* Sayfayı Bembeyaz Yap */
    .stApp { background-color: #FFFFFF !important; }

    /* Tüm Yazıları SİYAH ve OKUNUR Yap */
    h1, h2, h3, p, label, span, .stMarkdown, .stSelectbox p, .stNumberInput label {
        color: #000000 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
    }

    /* Giriş Kutularını Belirginleştir (Siyah Kutuları Siler) */
    input, div[data-baseweb="select"] {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 10px !important;
    }

    /* Ana Kart Tasarımı */
    .luxury-card {
        background: #FFFFFF !important;
        border: 3px solid #000000 !important;
        border-radius: 20px !important;
        padding: 30px !important;
        margin-bottom: 20px !important;
        box-shadow: 8px 8px 0px #FF0000 !important; /* Kırmızı Gölge */
    }

    /* Fiyat Paneli (Sarı) */
    .price-box {
        background-color: #FFCC00 !important;
        padding: 30px !important;
        border-radius: 15px !important;
        border: 4px solid #000000 !important;
        text-align: center !important;
        box-shadow: 6px 6px 0px #000000 !important;
    }
    
    .price-val { color: #000000 !important; font-size: 4rem !important; font-weight: 800 !important; margin: 0; }

    /* Kırmızı Buton */
    .stButton>button {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: 3px solid #000000 !important;
        height: 3.5em !important;
        text-transform: uppercase !important;
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
st.markdown("<h1 style='text-align: center; font-size: 4.5rem;'>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000 !important; margin-top:-20px;'>🏁 GERÇEK DEĞERİNİ ÖĞRENİN</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini Buraya Yapıştırın", height=200)
    if st.button("PİYASAYI ÇÖZ"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- ANALİZ FORMU ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("stable_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("📅 MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("🛣️ MEVCUT KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("⚙️ ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("💸 TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", ["Kaput", "Tavan", "Bagaj", "Yanlar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("DEĞERİNİ HESAPLA")

    if submit:
        df = st.session_state.data
        yil_verisi = df[df["Yıl"] == v_yil]
        
        # Dinamik Hesaplama
        katsayi = 4.0 if v_yil > 2021 else 3.5
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz = np.poly1d(z)(v_yil)
        km_ort = yil_verisi["KM"].mean() if not yil_verisi.empty else df["KM"].mean()
        
        final_price = (baz * 1.05) + (km_ort - v_km) * katsayi + (60000 if v_vites == "Otomatik" else -20000) - (v_hasar * 0.18 + len(v_boya)*9000 + len(v_degisen)*20000)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#FF0000; font-weight:800; margin:0;'>TAHMİNİ SATIŞ DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

        # WhatsApp Paylaşım
        paylasim = f"*Bİ'EDERİ ANALİZİ*\n🚗 {v_yil} Model | {v_km:,.0f} KM\n💰 Değer: {max(0, final_price):,.0f} TL"
        st.markdown(f'<a href="https://wa.me{urllib.parse.quote(paylasim)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; border-radius:10px; padding:10px; font-weight:800; cursor:pointer; border:3px solid #000;">📱 WHATSAPP İLE PAYLAŞ</button></a>', unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE"):
        del st.session_state.data
        st.rerun()
