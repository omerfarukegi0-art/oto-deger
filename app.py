import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Hassas Analiz", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #FFFFFF !important; font-family: sans-serif; font-weight: 800; text-align: center; font-size: 3.5rem !important; }
    .luxury-card {
        background-color: #161b22;
        padding: 2.5rem;
        border-radius: 25px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .trink-box { 
        background: linear-gradient(135deg, #FF0000 0%, #B20000 100%); 
        padding: 2.5rem; 
        border-radius: 25px; 
        text-align: center; 
        margin: 20px 0; 
        border: 2px solid #FFF;
    }
    .price-val { color: #FFFFFF; font-size: 3.8rem; font-weight: 900; margin: 0; line-height: 1.1; }
    .stButton>button {
        background-color: #FF0000 !important; color: white !important;
        font-weight: 800 !important; width: 100%; height: 4em; border-radius: 15px; border: none; text-transform: uppercase;
    }
    label { color: #d4af37 !important; font-weight: 700; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZİ ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    kms = [int(k.replace(".", "").replace(",", "")) for k in re.findall(r"\b(\d{1,3}[\.,]\d{3})\b", metin) if int(k.replace(".", "").replace(",", "")) not in fiyatlar]
    limit = min(len(fiyatlar), len(yillar), len(kms))
    if limit == 0: return pd.DataFrame()
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]}).drop_duplicates()

parcalar = ["Kaput", "Tavan", "Bagaj Kapağı", "Sol Ön Çamur.", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamur.", "Sağ Ön Çamur.", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamur."]

st.markdown("<h1>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>")

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini Buraya Yapıştırın", height=200)
    if st.button("ANALİZİ BAŞLAT"):
        if raw_input:
            st.session_state.data = veriyi_ayristir(raw_input)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("precision_trink"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=100000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", parcalar)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", parcalar)
        submit = st.form_submit_button("HASSAS DEĞERLEME YAP")

    if submit:
        df = st.session_state.data
        yil_daslar = df[df["Yıl"] == v_yil].copy()
        
        # --- HASSAS HESAPLAMA MOTORU ---
        if not yil_daslar.empty:
            # 1. KM'ye en yakın 5 emsali bul
            yil_daslar['Fark'] = (yil_daslar['KM'] - v_km).abs()
            yakın_emsaller = yil_daslar.sort_values(by='Fark').head(5)
            
            # 2. BAZ FİYAT: En yakın emsallerin ORTALAMASINI al (Sapmayı önlemek için)
            baz_pazar_fiyati = yakın_emsaller["Fiyat"].mean()
        else:
            z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
            baz_pazar_fiyati = np.poly1d(z)(v_yil)

        # 3. KONDİSYON DÜZELTMELERİ
        # Hatasızlık Bonusu: İlan ortalamaları genellikle boyalı araçları da kapsar. 
        # Eğer senin aracın HATASIZSA, piyasa ortalamasını %4 yukarı taşır.
        if not v_boya and not v_degisen and v_hasar == 0:
            baz_pazar_fiyati *= 1.04

        # Ekspertiz Kesintileri (Daha makul oranlar)
        boya_kaybi = len(v_boya) * (baz_pazar_fiyati * 0.008) # Her boya sadece %0.8 düşürür
        degisen_kaybi = len(v_degisen) * (baz_pazar_fiyati * 0.02) # Her değişen %2 düşürür
        tramer_kaybi = v_hasar * 0.10 # Tramerin %10'u
        
        # Pazar Rayici Oluşturma
        pazar_degeri = baz_pazar_fiyati - (boya_kaybi + degisen_kaybi + tramer_kaybi)
        
        # TRİNK MAKASI (Şeffaf Makas: %6.5)
        # Piyasa 825k ise, Trink teklifi 771k civarı olur (Gerçek kurumsal teklif).
        trink_fiyat = pazar_degeri * 0.935

        st.markdown(f"""
            <div class='trink-box'>
                <p style='color:#FFF; font-weight:700; opacity:0.8; margin-bottom:10px;'>TRİNK NAKİT TEKLİFİ</p>
                <h1 class='price-val'>{max(0, trink_fiyat):,.0f} TL</h1>
                <div style='margin-top:15px; border-top:1px solid rgba(255,255,255,0.2); padding-top:10px;'>
                    <p style='color:#FFF; font-size:1.1rem; font-weight:600;'>
                        Piyasa Rayiç Değeri: {max(0, pazar_degeri):,.0f} TL
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 LİSTEYİ TEMİZLE"):
        del st.session_state.data
        st.rerun()
