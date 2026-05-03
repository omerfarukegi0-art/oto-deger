import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- TEMA VE RENK AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | Akıllı Analiz", layout="centered")

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

# --- VERİ ANALİZ MOTORU ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    limit = min(len(fiyatlar), len(yillar))
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit]}).drop_duplicates()

ekspertiz_parcalari = ["Kaput", "Tavan", "Bagaj Kapağı", "Sağ Ön Çamurluk", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamurluk", "Sol Ön Çamurluk", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamurluk"]

st.markdown("<h1 style='text-align: center; font-size: 5rem; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000; font-weight: 900; font-size: 1.2rem; margin-top:-20px;'>🏁 AKILLI EKSPERTİZ & RENK ANALİZİ</p>", unsafe_allow_html=True)

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
    with st.form("akilli_form"):
        st.markdown("<h3 style='margin-top:0;'>🔍 Araç Kondisyonu</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
            v_renk = st.selectbox("DIŞ RENK", ["Popüler (Siyah/Beyaz/Gri)", "Lansman Rengi (Mavi/Kırmızı)", "Özel Renk / Mat", "Diğer"])
        with c2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ekspertiz_parcalari)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ekspertiz_parcalari)
        
        submit = st.form_submit_button("💰 HESAPLA")

    if submit:
        df = st.session_state.data
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz_fiyat = np.poly1d(z)(v_yil)
        
        # --- GELİŞMİŞ HESAPLAMA MANTIĞI ---
        # 1. Kondisyon Bonusu (Hatasız araçlar piyasa ortalamasının üstündedir)
        bonus = 0
        if not v_boya and not v_degisen and v_hasar == 0:
            bonus = baz_fiyat * 0.05 # Hatasızlık primi %5
        
        # 2. Renk Etkisi
        renk_etkisi = {"Popüler (Siyah/Beyaz/Gri)": 0, "Lansman Rengi (Mavi/Kırmızı)": 25000, "Özel Renk / Mat": 45000, "Diğer": -15000}[v_renk]
        
        # 3. Dengeli Hasar Kesintileri
        tramer_kesintisi = v_hasar * 0.22 # Tramerin %22'si değer kaybı
        kritik = ["Tavan", "Kaput"]
        boya_kesintisi = sum([20000 if p in kritik else 10000 for p in v_boya])
        degisen_kesintisi = sum([45000 if p in kritik else 25000 for p in v_degisen])
        
        vites_farki = 60000 if v_vites == "Otomatik" else -15000
        
        final_price = baz_fiyat + bonus + renk_etkisi + vites_farki - (tramer_kesintisi + boya_kesintisi + degisen_kesintisi)

        # SONUÇ PANELİ
        st.markdown(f"<div class='price-box'><p class='price-val'>{max(0, final_price):,.0f} TL</p></div>", unsafe_allow_html=True)

        # WHATSAPP PAYLAŞIM BUTONU
        paylasim_metni = f"*OTO-DEĞER RAPORU*\n🚗 Model: {v_yil}\n💰 Değer: {max(0, final_price):,.0f} TL\n🎨 Renk: {v_renk}\n🛠️ Boya/Değişen: {len(v_boya)} boya, {len(v_degisen)} değişen\n💸 Tramer: {v_hasar:,.0f} TL"
        whatsapp_url = f"https://wa.me{urllib.parse.quote(paylasim_metni)}"
        st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; border-radius:10px; padding:10px; font-weight:800; cursor:pointer; margin-bottom:20px;">📱 WHATSAPP İLE PAYLAŞ</button></a>', unsafe_allow_html=True)

        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        res = [
            ("Pazar Rayiç Bedeli", f"{baz_fiyat:,.0f} TL"),
            ("Hatasızlık Primi / Bonus", f"{bonus:+,.0f} TL"),
            ("Renk Opsiyon Farkı", f"{renk_etkisi:+,.0f} TL"),
            ("Ekspertiz Düşümü", f"- ( {tramer_kesintisi + boya_kesintisi + degisen_kesintisi:,.0f} ) TL")
        ]
        for label, val in res:
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #eee;'><span style='color:#FF0000; font-weight:800;'>{label}</span><span style='font-weight:700;'>{val}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE VE BAŞTAN BAŞLA"):
        del st.session_state.data
        st.rerun()
