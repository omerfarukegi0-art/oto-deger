import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- TEMA VE STİL ---
st.set_page_config(page_title="OTO-DEĞER | Emsal Analiz", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span, .stMarkdown, .stSelectbox, .stNumberInput, .stRadio {
        color: #000000 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .luxury-card {
        background: #FFFFFF !important; border: 3px solid #000000;
        border-radius: 20px; padding: 30px; margin-bottom: 25px; box-shadow: 10px 10px 0px #FF0000;
    }
    .price-box {
        background-color: #FFCC00; padding: 25px; border-radius: 15px;
        border: 4px solid #000000; text-align: center; margin: 20px 0; box-shadow: 8px 8px 0px #FF0000;
    }
    .price-val { color: #000000; font-size: 4.5rem; font-weight: 900; margin: 0; line-height: 1; }
    .stButton>button {
        background-color: #FF0000 !important; color: #FFFFFF !important;
        font-weight: 800; border-radius: 10px; border: 3px solid #000000; height: 3.5em; text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    kms = [int(k.replace(".", "")) for k in re.findall(r"\b(\d{1,3}\.\d{3})\b", metin)]
    limit = min(len(fiyatlar), len(yillar), len(kms))
    df = pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]})
    return df.drop_duplicates()

ekspertiz_parcalari = ["Kaput", "Tavan", "Bagaj Kapağı", "Sağ Ön Çamurluk", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamurluk", "Sol Ön Çamurluk", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamurluk"]

st.markdown("<h1 style='text-align: center; font-size: 5rem; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000 !important; font-weight: 900; font-size: 1.2rem; margin-top:-20px;'>🏁 EMSAL TABANLI PİYASA ANALİZİ</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini (Fiyat ve KM Dahil) Yapıştır", height=200)
    if st.button("🚀 PİYASAYI ÇÖZ"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    with st.form("emsal_form"):
        st.markdown("<h3 style='margin-top:0;'>🔍 Araç Detayları</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("ARACININ KİLOMETRESİ", value=100000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TOPLAM TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ekspertiz_parcalari)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ekspertiz_parcalari)
        
        submit = st.form_submit_button("💰 EMSALLERE GÖRE HESAPLA")

    if submit:
        df = st.session_state.data
        
        # --- EMSAL KARŞILAŞTIRMA MANTIĞI ---
        # 1. Aynı yıl ve yakın kilometredeki (±25k KM) ilanları bul
        emsaller = df[(df["Yıl"] == v_yil) & (df["KM"] >= v_km - 25000) & (df["KM"] <= v_km + 25000)]
        
        if len(emsaller) >= 3:
            # Eğer yeterli emsal varsa, o emsallerin ortalamasını baz al (En gerçekçi sonuç)
            emsal_baz_fiyat = emsaller["Fiyat"].mean()
            mesaj = f"Kendi modelinde ve kilonmetrende {len(emsaller)} emsal ilan baz alındı."
        else:
            # Eğer emsal azsa, yıla göre genel trendi hesapla ve KM düzeltmesi yap
            z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
            emsal_baz_fiyat = np.poly1d(z)(v_yil)
            # KM düzeltmesi (Piyasa ortalamasından senin KM'ne çekme)
            piyasa_km_ort = df[df["Yıl"] == v_yil]["KM"].mean() if not df[df["Yıl"] == v_yil].empty else df["KM"].mean()
            emsal_baz_fiyat += (piyasa_km_ort - v_km) * 3.5
            mesaj = "Yeterli emsal bulunamadı, pazar geneline göre hesaplandı."

        # 2. Kondisyon ve Diğer Düzeltmeler
        vites_farki = 50000 if v_vites == "Otomatik" else -15000
        tramer_kesintisi = v_hasar * 0.18
        boya_kesintisi = len(v_boya) * 8500
        degisen_kesintisi = len(v_degisen) * 20000
        
        # Hatasızlık Bonusu (Eğer piyasa ortalamasından (emsalden) geliyorsa bonus daha düşüktür)
        bonus = emsal_baz_fiyat * 0.03 if (not v_boya and not v_degisen and v_hasar == 0) else 0

        final_price = emsal_baz_fiyat + bonus + vites_farki - (tramer_kesintisi + boya_kesintisi + degisen_kesintisi)

        st.markdown(f"""
            <div class='price-box'>
                <p class='price-label'>EMSALLERE GÖRE DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
                <p style='margin:0; font-size:0.8rem; opacity:0.7;'>{mesaj}</p>
            </div>
        """, unsafe_allow_html=True)

        paylasim = f"*OTO-DEĞER EMSAL RAPORU*\n🚗 {v_yil} Model | {v_km:,.0f} KM\n💰 Piyasa Değeri: {max(0, final_price):,.0f} TL"
        st.markdown(f'<a href="https://wa.me{urllib.parse.quote(paylasim)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; border-radius:10px; padding:10px; font-weight:800; cursor:pointer; border:3px solid #000;">📱 SONUCU PAYLAŞ</button></a>', unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE"):
        del st.session_state.data
        st.rerun()
