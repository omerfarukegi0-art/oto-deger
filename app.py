import streamlit as st
import pandas as pd
import numpy as np
import re

# --- KURUMSAL SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Trink Sat", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #FFFFFF !important; font-family: sans-serif; font-weight: 800; text-align: center; font-size: 3.5rem !important; }
    
    .luxury-card {
        background-color: #161b22;
        padding: 2.5rem;
        border-radius: 25px;
        border: 1px solid #30363d;
        box-shadow: 0 15px 40px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    /* Trink Sat Kırmızı Panel */
    .trink-box { 
        background: linear-gradient(135deg, #FF0000 0%, #B20000 100%); 
        padding: 3rem; 
        border-radius: 25px; 
        text-align: center; 
        margin: 25px 0; 
        border: 3px solid #FFF;
        box-shadow: 0 10px 40px rgba(255, 0, 0, 0.4);
    }
    
    .price-val { color: #FFFFFF; font-size: 4rem; font-weight: 900; margin: 0; line-height: 1; }
    
    .stButton>button {
        background-color: #FF0000 !important; color: white !important;
        font-weight: 800 !important; width: 100%; height: 4em; border-radius: 15px; border: none; text-transform: uppercase;
    }
    label { color: #d4af37 !important; font-weight: 700; font-size: 0.85rem; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZİ ---
def veriyi_ayristir(metin):
    fiyatlar = [int(f.replace(".", "")) for f in re.findall(r"([\d\.]+)\s*TL", metin)]
    yillar = [int(y) for y in re.findall(r"\b(20[0-2][0-9])\b", metin)]
    # Sadece fiyatlarla karışmayan sayıları KM olarak al
    kms = [int(k.replace(".", "").replace(",", "")) for k in re.findall(r"\b(\d{1,3}[\.,]\d{3})\b", metin) if int(k.replace(".", "").replace(",", "")) not in fiyatlar]
    limit = min(len(fiyatlar), len(yillar), len(kms))
    if limit == 0: return pd.DataFrame()
    return pd.DataFrame({"Yıl": yillar[:limit], "Fiyat": fiyatlar[:limit], "KM": kms[:limit]}).drop_duplicates()

parcalar = ["Kaput", "Tavan", "Bagaj Kapağı", "Sol Ön Çamur.", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamur.", "Sağ Ön Çamur.", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamur."]

# --- HEADER ---
st.markdown("<h1>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>")
st.markdown("<p style='text-align:center; color:#FF0000; font-weight:800; letter-spacing:5px; margin-top:-20px;'>TRİNK SAT ALGORİTMASI</p>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 Piyasa İlanlarını Buraya Yapıştırın", height=200, placeholder="Sahibinden listesini kopyalayıp buraya bırakın...")
    if st.button("PİYASA VERİLERİNİ ÇÖZ"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("trink_engine"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("KİLOMETRE", value=50000, step=5000)
            v_vites = st.radio("ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("TRAMER (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", parcalar)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", parcalar)
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("TRİNK NAKİT TEKLİFİ AL")

    if submit:
        df = st.session_state.data
        yil_daslar = df[df["Yıl"] == v_yil].copy()
        
        # --- TRİNK SAT MATEMATİĞİ ---
        if not yil_daslar.empty:
            # 1. Aşama: En ucuz ilanları baz al (%25 kuantil)
            # Çünkü Trink Sat "en hızlı satılacak fiyattan" alım yapar.
            base_fiyat = yil_daslar["Fiyat"].quantile(0.25)
            
            # 2. Aşama: KM Düzeltmesi (İlanların ortalama KM'sine göre)
            km_ort = yil_daslar["KM"].mean()
            km_farki = km_ort - v_km
            km_etkisi = km_farki * 4.2 # Her 1 KM farkı 4.2 TL değer üretir
            
            baz_fiyat_km_dahil = base_fiyat + km_etkisi
        else:
            z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
            baz_fiyat_km_dahil = np.poly1d(z)(v_yil) * 0.92 # Emsal yoksa %8 kır

        # 3. Aşama: Kurumsal Ekspertiz Kesintileri (Daha sert)
        # Kritik parçalar (Tavan/Kaput) %4, diğerleri %2 düşürür
        boya_orani = sum([0.04 if p in ["Tavan", "Kaput"] else 0.02 for p in v_boya])
        degisen_orani = sum([0.08 if p in ["Tavan", "Kaput"] else 0.045 for p in v_degisen])
        
        # Toplam pazar değeri
        pazar_degeri = baz_fiyat_km_dahil * (1 - (boya_orani + degisen_orani))
        pazar_degeri -= (v_hasar * 0.25) # Tramerin %25'ini değer kaybı olarak düş
        if v_vites == "Otomatik": pazar_degeri += 75000
        
        # TRİNK SAT MAKASI: %9 Operasyonel kesinti (Nakit alım payı)
        trink_fiyat = pazar_degeri * 0.91

        # --- SONUÇ PANELİ ---
        st.markdown(f"""
            <div class='trink-box'>
                <p style='color:#FFF; font-weight:700; opacity:0.8; margin-bottom:10px; letter-spacing:2px;'>ANINDA NAKİT ALIM TEKLİFİ</p>
                <h1 class='price-val'>{max(0, trink_fiyat):,.0f} TL</h1>
                <p style='color:#FFF; font-size:0.9rem; margin-top:15px; opacity:0.7;'>
                    Piyasa Rayiç Bedeli: {max(0, pazar_degeri):,.0f} TL
                </p>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 YENİ HESAPLAMA"):
        del st.session_state.data
        st.rerun()
