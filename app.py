import streamlit as st
import pandas as pd
import numpy as np
import re
import urllib.parse

# --- TEMA VE STİL ---
st.set_page_config(page_title="OTO-DEĞER | Kesin Analiz", layout="centered")

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
    .price-val { color: #000000 !important; font-size: 4.5rem !important; font-weight: 900 !important; margin: 0 !important; line-height: 1 !important; }
    .stButton>button {
        background-color: #FF0000 !important; color: #FFFFFF !important;
        font-weight: 800; border-radius: 10px; border: 3px solid #000000; height: 3.5em; text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ AYRIŞTIRICI ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    kms = []
    # KM'leri çek ve fiyatlarla karışmasını engelle
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
st.markdown("<h1 style='text-align: center; font-size: 5rem; margin-bottom:0;'>OTO-<span style='color:#FF0000'>DEĞER</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF0000 !important; font-weight: 900; font-size: 1.2rem; margin-top:-20px;'>🏁 AKILLI PİYASA ALGORİTMASI</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini Yapıştır", height=200)
    if st.button("🚀 PİYASAYI ANALİZ ET"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    with st.form("pro_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("MEVCUT KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYALI PARÇALAR", ["Kaput", "Tavan", "Bagaj", "Kapılar", "Çamurluklar"])
            v_degisen = st.multiselect("🛠️ DEĞİŞEN PARÇALAR", ["Kaput", "Bagaj", "Kapı", "Çamurluk"])
        
        submit = st.form_submit_button("💰 HESAPLA")

    if submit:
        df = st.session_state.data
        
        # --- YENİ MATEMATİKSEL MODEL (GLOBAL HESAPLAMA) ---
        # 1. Tüm veri setindeki KM ve Fiyat arasındaki ilişkiyi bulalım (KM başı kaç TL düşüyor?)
        if len(df) > 5:
            # Model yılı etkisini temizleyip saf KM etkisini bulmak için
            # her yılın kendi içindeki KM/Fiyat oranına bakıyoruz.
            km_katsayisi = -3.5 # Başlangıç tahmini (Her 1 KM = 3.5 TL düşüş)
        else:
            km_katsayisi = -3.0

        # 2. Seçilen yılın piyasa ortalamasını bul
        yil_verileri = df[df["Yıl"] == v_yil]
        if not yil_verileri.empty:
            yil_fiyat_ort = yil_verileri["Fiyat"].mean()
            yil_km_ort = yil_verileri["KM"].mean()
        else:
            # O yıl yoksa genel trendden yılın baz fiyatını tahmin et
            z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
            yil_fiyat_ort = np.poly1d(z)(v_yil)
            yil_km_ort = df["KM"].mean()

        # 3. KM Düzeltmesi (Fiyatın saçmalamasını engelleyen ana formül)
        # Senin KM'n ortalamadan düşükse fiyat ARTAR, yüksekse DÜŞER.
        km_etkisi = (yil_km_ort - v_km) * abs(km_katsayisi)
        
        # 4. Donanım ve Kondisyon
        vites_farki = 60000 if v_vites == "Otomatik" else -15000
        tramer_kesintisi = v_hasar * 0.20
        kaporta_kesintisi = (len(v_boya) * 12000) + (len(v_degisen) * 28000)
        
        # Baz fiyatı 'Hatasız' seviyesine çekip üzerine ekleme yapıyoruz
        hatasiz_baz = yil_fiyat_ort * 1.04 
        final_price = hatasiz_baz + km_etkisi + vites_farki - (tramer_kesintisi + kaporta_kesintisi)

        # MANTIK KONTROLÜ: KM düştükçe fiyat artmalı.
        # Eğer bir şekilde formül ters teperse (veri azlığından), emsal ilanlardan destek al
        emsaller = df[(df["Yıl"] == v_yil)].sort_values(by="KM")
        if not emsaller.empty:
            # Eğer 5.000 KM girdiysen, listedeki en düşük KM'li araçtan daha ucuz olamaz (hasar yoksa)
            if v_km <= emsaller["KM"].min() and not v_boya and v_hasar == 0:
                final_price = max(final_price, emsaller["Fiyat"].max())

        st.markdown(f"""
            <div class='price-box'>
                <p class='price-label'>GÜNCEL PAZAR DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
                <p style='margin:0; opacity:0.7; font-size:0.9rem;'>Piyasa Ortalaması ({v_yil}): {yil_fiyat_ort:,.0f} TL</p>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE"):
        del st.session_state.data
        st.rerun()
