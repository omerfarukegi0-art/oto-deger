import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Piyasa Analiz", layout="centered")

# --- LÜKS TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #FFFFFF !important; font-family: sans-serif; font-weight: 800; text-align: center; font-size: 4rem !important; }
    .luxury-card {
        background-color: #161b22;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #30363d;
        border-left: 5px solid #FF0000;
        margin-bottom: 20px;
    }
    .emsal-card {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #30363d;
    }
    .price-box { background-color: #FFCC00; padding: 2rem; border-radius: 20px; text-align: center; margin: 20px 0; border: 3px solid #000; }
    .price-val { color: #000000; font-size: 3.5rem; font-weight: 800; margin: 0; }
    .stButton>button {
        background-color: #FF0000 !important; color: white !important;
        font-weight: 700 !important; width: 100%; height: 3.8em; border-radius: 12px; border: none; text-transform: uppercase;
    }
    label { color: #d4af37 !important; font-weight: 700; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

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

parcalar = ["Kaput", "Tavan", "Bagaj Kapağı", "Sol Ön Çamur.", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamur.", "Sağ Ön Çamur.", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamur."]

st.markdown("<h1>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini Buraya Yapıştırın", height=200)
    if st.button("PİYASAYI ANALİZ ET"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("lider_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("🛣️ ARACININ KİLOMETRESİ", value=50000, step=5000)
            v_vites = st.radio("⚙️ ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("💸 TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", parcalar)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", parcalar)
        submit = st.form_submit_button("GERÇEK DEĞERİ HESAPLA")

    if submit:
        df = st.session_state.data
        yil_daslar = df[df["Yıl"] == v_yil].copy()
        
        if not yil_daslar.empty:
            # 1. EN YAKIN 7 İLANI AL
            yil_daslar['Fark'] = (yil_daslar['KM'] - v_km).abs()
            emsaller = yil_daslar.sort_values(by='Fark').head(7)
            
            # 2. ÜST DİLİM STRATEJİSİ: En ucuz %30'u "hasarlı/acil" diye ele.
            # Kalan ilanların (Piyasanın düzgün araçları) ortalamasını al.
            alt_sinir = emsaller["Fiyat"].quantile(0.30)
            temiz_emsaller = emsaller[emsaller["Fiyat"] >= alt_sinir]
            baz_fiyat = temiz_emsaller["Fiyat"].mean()
            notu = "Piyasadaki düşük fiyatlı/hasarlı ilanlar elenerek 'temiz emsal' baz alındı."
        else:
            z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
            baz_fiyat = np.poly1d(z)(v_yil) * 1.05 # Veri yoksa %5 yukarıdan başla
            notu = "Emsal veri azlığı nedeniyle pazar trendi yukarı yönlü hesaplandı."

        # 3. GÜÇLÜ KONDİSYON PRİMİ
        # Hatasız araç piyasada her zaman paradır.
        bonus = baz_fiyat * 0.06 if (not v_boya and not v_degisen and v_hasar == 0) else 0
        vites_farki = 65000 if v_vites == "Otomatik" else -25000
        
        # Kesintileri daha da yumuşattık (Piyasa artık ufak boyaya fiyat öldürmüyor)
        kesinti = (v_hasar * 0.10) + (len(v_boya) * 6000) + (len(v_degisen) * 15000)
        
        final_price = baz_fiyat + bonus + vites_farki - kesinti

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:700; opacity:0.6;'>GÜNCEL PAZAR DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
                <p style='margin:0; font-size:0.8rem; color:#444;'>{notu}</p>
            </div>
        """, unsafe_allow_html=True)

        if not yil_daslar.empty:
            st.markdown("### 🔍 Referans Alınan Temiz Emsaller")
            for _, row in temiz_emsaller.head(3).iterrows():
                st.markdown(f"<div class='emsal-card'><span style='color:#FFF;'>{row['Yıl']} • {row['KM']:,.0f} KM</span><span style='color:#FFCC00; font-weight:800; float:right;'>{row['Fiyat']:,.0f} TL</span></div>", unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
