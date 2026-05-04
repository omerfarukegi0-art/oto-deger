import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- TEMA AYARLARI ---
st.set_page_config(page_title="OTO-DEĞER | Birebir Analiz", layout="centered")

st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span, .stMarkdown, .stSelectbox, .stNumberInput, .stRadio {
        color: #000000 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .luxury-card {
        background: #FFFFFF !important; border: 3px solid #000000 !important;
        border-radius: 20px !important; padding: 30px !important;
        margin-bottom: 25px !important; box-shadow: 10px 10px 0px #FF0000 !important;
    }
    .price-box {
        background-color: #FFCC00 !important; padding: 25px !important;
        border-radius: 15px !important; border: 4px solid #000000 !important;
        text-align: center !important; margin: 20px 0 !important; box-shadow: 8px 8px 0px #FF0000 !important;
    }
    .price-val { color: #000000 !important; font-size: 4.5rem !important; font-weight: 900 !important; margin: 0 !important; line-height: 1 !important; }
    .stButton>button {
        background-color: #FF0000 !important; color: #FFFFFF !important;
        font-weight: 800 !important; border-radius: 10px !important;
        border: 3px solid #000000 !important; height: 3.5em !important; text-transform: uppercase !important;
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
st.markdown("<p style='text-align: center; color: #FF0000 !important; font-weight: 900; font-size: 1.2rem; margin-top:-20px;'>🏁 NOKTA ATIŞI FİYATLANDIRMA</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini Buraya Yapıştır", height=200)
    if st.button("🚀 PİYASAYI ÇÖZ"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    with st.form("hassas_form"):
        st.markdown("<h3 style='margin-top:0;'>🔍 Aracın Gerçek Durumu</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
            v_renk = st.selectbox("DIŞ RENK", ["Standart (Beyaz/Gri)", "Lansman (Mavi/Kırmızı)", "Özel Renk (Mat/Metalik)"])
        with col2:
            v_hasar = st.number_input("TOPLAM TRAMER (TL)", value=0, step=1000)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ekspertiz_parcalari)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ekspertiz_parcalari)
        
        submit = st.form_submit_button("💰 TAM DEĞERİNİ HESAPLA")

    if submit:
        df = st.session_state.data
        # 1. Baz Fiyatı (Hatasız bazda) hesapla
        z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
        baz_fiyat = np.poly1d(z)(v_yil)
        
        # Piyasa ortalamasını 'Hatasız' fiyata çekmek için %6 prim ekliyoruz
        hatasiz_baz = baz_fiyat * 1.06 
        
        # 2. Renk ve Vites
        renk_etkisi = {"Standart (Beyaz/Gri)": 0, "Lansman (Mavi/Kırmızı)": 20000, "Özel Renk (Mat/Metalik)": 45000}[v_renk]
        vites_farki = 55000 if v_vites == "Otomatik" else -20000
        
        # 3. Gerçekçi Ekspertiz Düşümleri (Birebir Pazar Uyumu)
        tramer_etkisi = v_hasar * 0.20 # Hasar kaydının %20'si gerçek değer kaybıdır
        kritik = ["Tavan", "Kaput", "Bagaj Kapağı"]
        
        # Boya: Kritik parçalar 18k, diğerleri 10k
        boya_dususu = sum([18000 if p in kritik else 10000 for p in v_boya])
        # Değişen: Kritik parçalar 40k, diğerleri 22k
        degisen_dususu = sum([40000 if p in kritik else 22000 for p in v_degisen])
        
        # NİHAİ HESAPLAMA
        final_price = hatasiz_baz + vites_farki + renk_etkisi - (tramer_etkisi + boya_dususu + degisen_dususu)

        st.markdown(f"""
            <div class='price-box'>
                <p class='price-label'>ARACININ PAZAR DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
            </div>
        """, unsafe_allow_html=True)

        paylasim = f"*OTO-DEĞER NOKTA ATIŞI ANALİZ*\n🚗 {v_yil} Model\n💰 Değer: {max(0, final_price):,.0f} TL\n🛠️ Ekspertiz: {len(v_boya)} Boya / {len(v_degisen)} Değişen"
        st.markdown(f'<a href="https://wa.me{urllib.parse.quote(paylasim)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; border-radius:10px; padding:10px; font-weight:800; cursor:pointer; border:3px solid #000;">📱 SONUCU PAYLAŞ</button></a>', unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE"):
        del st.session_state.data
        st.rerun()
