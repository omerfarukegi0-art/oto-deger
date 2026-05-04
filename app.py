import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- TEMA AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | Dengeli", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, label, .stMarkdown, .stSelectbox, .stNumberInput, .stRadio {
        color: #000000 !important; font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .luxury-card {
        background: #FFFFFF; border: 3px solid #000000; border-radius: 20px;
        padding: 30px; margin-bottom: 25px; box-shadow: 10px 10px 0px #FF0000;
    }
    .price-box {
        background-color: #FFCC00; padding: 20px; border-radius: 15px;
        border: 4px solid #000000; text-align: center; margin: 20px 0; box-shadow: 8px 8px 0px #FF0000;
    }
    .price-val { color: #000000; font-size: 4.5rem; font-weight: 900; margin: 0; line-height: 1; }
    .stButton>button {
        background-color: #FF0000 !important; color: #FFFFFF !important;
        font-weight: 800; border-radius: 10px; border: 3px solid #000000;
    }
    </style>
    """, unsafe_allow_html=True)

def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    limit = min(len(fiyatlar), len(yillar))
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit]}).drop_duplicates()

ekspertiz_parcalari = ["Kaput", "Tavan", "Bagaj Kapağı", "Sağ Ön Çamurluk", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamurluk", "Sol Ön Çamurluk", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamurluk"]

st.markdown("<h1 style='text-align: center; font-size: 5rem; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000; font-weight: 900; font-size: 1.2rem; margin-top:-20px;'>🏁 DENGELİ PİYASA ANALİZİ</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Verilerini Yapıştır", height=200)
    if st.button("🚀 PİYASAYI ÇÖZ"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("dengeli_form"):
        st.markdown("<h3 style='margin-top:0;'>🔍 Araç Durumu</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
            v_renk = st.selectbox("DIŞ RENK", ["Standart", "Lansman Rengi (+)", "Özel Renk (++)"])
        with c2:
            v_hasar = st.number_input("TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", ekspertiz_parcalari)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", ekspertiz_parcalari)
        
        submit = st.form_submit_button("💰 HESAPLA")

    if submit:
        df = st.session_state.data
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz_fiyat = np.poly1d(z)(v_yil)
        
        # --- YENİ DENGELİ HESAPLAMA MOTORU ---
        # 1. Hatasızlık Bonusu (Eğer araç tertemizse ortalamayı %4 yukarı çeker)
        bonus = baz_fiyat * 0.04 if (not v_boya and not v_degisen and v_hasar == 0) else 0
        
        # 2. Renk Etkisi
        renk_farki = {"Standart": 0, "Lansman Rengi (+)": 15000, "Özel Renk (++)": 30000}[v_renk]
        
        # 3. Şanzıman (Baz fiyata göre dengeleme)
        vites_farki = 45000 if v_vites == "Otomatik" else -15000
        
        # 4. Ekspertiz Düzeltmesi (Yumuşatılmış Katsayılar)
        tramer_etkisi = v_hasar * 0.15 # Tramerin sadece %15'i fiyata eksi yazar
        kritik = ["Tavan", "Kaput"]
        # Normal parçalar 7 bin, kritik parçalar 15 bin TL düşer (Daha insafı rakamlar)
        boya_etkisi = sum([15000 if p in kritik else 7000 for p in v_boya])
        degisen_etkisi = sum([30000 if p in kritik else 15000 for p in v_degisen])
        
        final_price = baz_fiyat + bonus + renk_farki + vites_farki - (tramer_etkisi + boya_etkisi + degisen_etkisi)

        st.markdown(f"<div class='price-box'><p class='price-val'>{max(0, final_price):,.0f} TL</p></div>", unsafe_allow_html=True)

        # WHATSAPP
        paylasim = f"*OTO-DEĞER RAPORU*\n🚗 Yıl: {v_yil}\n💰 Değer: {max(0, final_price):,.0f} TL\n🛠️ Ekspertiz: {len(v_boya)} Boya / {len(v_degisen)} Değişen"
        st.markdown(f'<a href="https://wa.me{urllib.parse.quote(paylasim)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; border-radius:10px; padding:10px; font-weight:800; cursor:pointer; margin-bottom:20px;">📱 WHATSAPP İLE PAYLAŞ</button></a>', unsafe_allow_html=True)

        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        res = [
            ("Pazar Rayiç Bedeli", f"{baz_fiyat:,.0f} TL"),
            ("Kondisyon Primi", f"{bonus:+,.0f} TL"),
            ("Ekspertiz Düzeltmesi", f"- ( {tramer_etkisi + boya_etkisi + degisen_etkisi:,.0f} ) TL"),
            ("Acil Satış Bedeli", f"{(final_price * 0.94):,.0f} TL")
        ]
        for label, val in res:
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #eee;'><span style='color:#FF0000; font-weight:800;'>{label}</span><span style='font-weight:700;'>{val}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔄 BAŞTAN BAŞLA"):
        del st.session_state.data
        st.rerun()
