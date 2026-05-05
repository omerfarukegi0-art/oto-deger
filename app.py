import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Dengeli Analiz", layout="centered")

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

parcalar = ["Kaput", "Tavan", "Bagaj Kapağı", "Sol Ön Çamur.", "Sol Ön Kapı", "Sol Arka Kapı", "Sol Arka Çamur.", "Sağ Ön Çamurluk", "Sağ Ön Kapı", "Sağ Arka Kapı", "Sağ Arka Çamur."]

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
    with st.form("dengeli_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("🛣️ ARACININ KİLOMETRESİ", value=50000, step=5000)
            v_vites = st.radio("⚙️ ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("💸 TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", parcalar)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", parcalar)
        submit = st.form_submit_button("DENGELİ DEĞERLEME YAP")

    if submit:
        df = st.session_state.data
        yil_daslar = df[df["Yıl"] == v_yil].copy()
        
        if not yil_daslar.empty:
            # 1. KM'YE EN YAKIN 10 İLANI AL (Geniş havuz)
            yil_daslar['Fark'] = (yil_daslar['KM'] - v_km).abs()
            emsal_havuzu = yil_daslar.sort_values(by='Fark').head(10)
            
            # 2. UÇLARI ELE (En pahalı %20 ve en ucuz %20'yi at)
            # Bu sayede hem 'uçan' fiyatlar hem de 'hasarlı' ucuz ilanlar elenir.
            alt_sinir = emsal_havuzu["Fiyat"].quantile(0.20)
            ust_sinir = emsal_havuzu["Fiyat"].quantile(0.80)
            temiz_emsaller = emsal_havuzu[(emsal_havuzu["Fiyat"] >= alt_sinir) & (emsal_havuzu["Fiyat"] <= ust_sinir)]
            
            # Eğer filtreleme sonrası veri kalmazsa havuzun medyanını al
            baz_fiyat = temiz_emsaller["Fiyat"].median() if not temiz_emsaller.empty else emsal_havuzu["Fiyat"].median()
            notu = "Piyasadaki uç fiyatlar elenerek, gerçekçi orta segment baz alındı."
        else:
            z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
            baz_fiyat = np.poly1d(z)(v_yil)
            notu = "Model yılında veri azlığı nedeniyle pazar eğilimi hesaplandı."

        # 3. KONDİSYON DÜZELTMELERİ (Hatasız araç seçildiyse ufak bir prim ekle)
        hatasizlik_bonusu = baz_fiyat * 0.03 if (not v_boya and not v_degisen and v_hasar == 0) else 0
        vites_farki = 55000 if v_vites == "Otomatik" else -20000
        
        # Ekspertiz Düşümleri (Makul seviyede)
        tramer_kesintisi = v_hasar * 0.12
        boya_kesintisi = len(v_boya) * 7500
        degisen_kesintisi = len(v_degisen) * 18000
        
        final_price = baz_fiyat + hatasizlik_bonusu + vites_farki - (tramer_kesintisi + boya_kesintisi + degisen_kesintisi)

        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:700; opacity:0.6;'>GERÇEKÇİ PAZAR DEĞERİ</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
                <p style='margin:0; font-size:0.8rem; color:#444;'>{notu}</p>
            </div>
        """, unsafe_allow_html=True)

        if not yil_daslar.empty:
            st.markdown("### 🔍 Referans Alınan Piyasa Emsalleri")
            for _, row in emsal_havuzu.head(3).iterrows():
                st.markdown(f"<div class='emsal-card'><span style='color:#FFF;'>{row['Yıl']} • {row['KM']:,.0f} KM</span><span style='color:#FFCC00; font-weight:800; float:right;'>{row['Fiyat']:,.0f} TL</span></div>", unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
