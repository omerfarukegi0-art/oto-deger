import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- TEMA VE RENK AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | Sport", layout="centered")

# Yazıların görünmeme sorununu kökten çözen ve sayfayı bembeyaz yapan CSS
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* Sayfayı bembeyaz yap */
    .stApp { background-color: #FFFFFF !important; }

    /* Tüm metinlerin rengini SİYAH olarak zorla */
    h1, h2, h3, p, label, span, .stMarkdown, .stSelectbox, .stNumberInput, .stRadio {
        color: #000000 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Lüks Kart Tasarımı */
    .luxury-card {
        background: #FFFFFF !important;
        border: 3px solid #000000 !important;
        border-radius: 20px !important;
        padding: 30px !important;
        margin-bottom: 25px !important;
        box-shadow: 10px 10px 0px #FF0000 !important; /* Kırmızı Sert Gölge */
    }

    /* Fiyat Paneli (Sarı Üzerine Siyah Yazı) */
    .price-box {
        background-color: #FFCC00 !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border: 4px solid #000000 !important;
        text-align: center !important;
        margin: 20px 0 !important;
        box-shadow: 8px 8px 0px #FF0000 !important;
    }
    .price-label { color: #FF0000 !important; font-weight: 800 !important; letter-spacing: 2px !important; margin-bottom: 5px !important; }
    .price-val { color: #000000 !important; font-size: 4.5rem !important; font-weight: 900 !important; margin: 0 !important; line-height: 1 !important; }

    /* Kırmızı Butonlar */
    .stButton>button {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: 3px solid #000000 !important;
        height: 3.5em !important;
        text-transform: uppercase !important;
        width: 100% !important;
    }

    /* Liste Satırları */
    .info-line {
        display: flex;
        justify-content: space-between;
        padding: 15px 0;
        border-bottom: 2px solid #EEEEEE;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ MOTORU ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    limit = min(len(fiyatlar), len(yillar))
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit]}).drop_duplicates()

ekspertiz_parcalari = ["Kaput", "Tavan", "Bagaj Kapağı", "Sağ Ön Çamurluk", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamurluk", "Sol Ön Çamurluk", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamurluk"]

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center; font-size: 5rem; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000 !important; font-weight: 900; font-size: 1.2rem; margin-top:-20px;'>🏁 HIZLI PİYASA ANALİZ SİSTEMİ</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📋 İlan Listesini Yapıştır</h3>", unsafe_allow_html=True)
    raw_input = st.text_area("", height=200, placeholder="Sahibinden'den kopyaladığınız metni buraya yapıştırın...")
    if st.button("🚀 PİYASAYI ÇÖZ"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- ANALİZ FORMU ---
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("main_form"):
        st.markdown("<h3 style='margin-top:0;'>🔍 Araç Kondisyonu</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
            v_renk = st.selectbox("DIŞ RENK", ["Standart", "Lansman Rengi (+)", "Özel Renk (++)"])
        with col2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ekspertiz_parcalari)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ekspertiz_parcalari)
        
        submit = st.form_submit_button("💰 HESAPLA")

    if submit:
        df = st.session_state.data
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz_fiyat = np.poly1d(z)(v_yil)
        
        # Dengeleme Mantığı
        bonus = baz_fiyat * 0.04 if (not v_boya and not v_degisen and v_hasar == 0) else 0
        renk_farki = {"Standart": 0, "Lansman Rengi (+)": 15000, "Özel Renk (++)": 30000}[v_renk]
        vites_farki = 45000 if v_vites == "Otomatik" else -15000
        
        # Yumuşatılmış Ekspertiz Düşümleri
        tramer_kesintisi = v_hasar * 0.18
        boya_kesintisi = len(v_boya) * 8000
        degisen_kesintisi = len(v_degisen) * 18000
        
        final_price = baz_fiyat + bonus + renk_farki + vites_farki - (tramer_kesintisi + boya_kesintisi + degisen_kesintisi)

        # --- SONUÇ PANELİ ---
        st.markdown(f"""
            <div class='price-box'>
                <p class='price-label'>TAHMİNİ RAYİÇ BEDEL</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

        # WHATSAPP PAYLAŞIM
        paylasim = f"*OTO-DEĞER RAPORU*\n🚗 Yıl: {v_yil}\n💰 Değer: {max(0, final_price):,.0f} TL"
        st.markdown(f'<a href="https://wa.me{urllib.parse.quote(paylasim)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; border-radius:10px; padding:10px; font-weight:800; cursor:pointer; margin-bottom:20px; border:3px solid #000;">📱 WHATSAPP İLE PAYLAŞ</button></a>', unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE"):
        del st.session_state.data
        st.rerun()
