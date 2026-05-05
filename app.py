import streamlit as st
import pandas as pd
import numpy as np
import re

# --- SAYFA AYARI ---
st.set_page_config(page_title="Bİ'EDERİ | Eksper Analiz", layout="centered")

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
        font-weight: 700; width: 100%; height: 3.8em; border-radius: 12px; border: none; text-transform: uppercase;
    }
    label { color: #d4af37 !important; font-weight: 700; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ANALİZİ ---
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

# --- ANA EKRAN ---
st.markdown("<h1>Bİ'<span style='color:#FF0000'>EDERİ</span></h1>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    raw_input = st.text_area("📋 İlan Listesini Buraya Yapıştırın", height=200)
    if st.button("PİYASAYI ÇÖZ"):
        if raw_input:
            temp_df = veriyi_ayristir(raw_input)
            if not temp_df.empty:
                st.session_state.data = temp_df
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
    with st.form("perfection_form"):
        col1, col2 = st.columns(2)
        with col1:
            v_yil = st.selectbox("MODEL YILI", sorted(st.session_state.data["Yıl"].unique(), reverse=True))
            v_km = st.number_input("🛣️ ARACININ KİLOMETRESİ", value=50000, step=5000)
            v_vites = st.radio("⚙️ ŞANZIMAN", ["Otomatik", "Manuel"], horizontal=True)
        with col2:
            v_hasar = st.number_input("💸 TRAMER KAYDI (TL)", value=0)
            v_boya = st.multiselect("🎨 BOYA", parcalar)
            v_degisen = st.multiselect("🛠️ DEĞİŞEN", parcalar)
        
        st.write("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("HASSAS DEĞERLEME YAP")

    if submit:
        df = st.session_state.data
        
        # --- GELİŞMİŞ EMSAL TEMİZLEME ALGORİTMASI ---
        yil_daslar = df[df["Yıl"] == v_yil].copy()
        
        if not yil_daslar.empty:
            # Senin KM'ne yakın emsalleri bul (±25k KM)
            yil_daslar['Fark'] = (yil_daslar['KM'] - v_km).abs()
            yakin_emsaller = yil_daslar.sort_values(by='Fark').head(5) # En yakın 5 ilanı al
            
            # BU 5 İLANDAN EN PAHALI 2 TANESİNİ SEÇ (Büyük ihtimalle hatasız olanlar bunlardır)
            hatasiz_emsaller = yakin_emsaller.sort_values(by='Fiyat', ascending=False).head(2)
            hatasiz_baz_fiyat = hatasiz_emsaller["Fiyat"].mean()
            
            emsal_notu = f"Piyasadaki en yüksek fiyatlı (hatasız kabul edilen) {len(hatasiz_emsaller)} ilan baz alındı."
        else:
            # Emsal yoksa genel trendi kullan
            z = np.polyfit(df["Yıl"], df["Fiyat"], 1)
            hatasiz_baz_fiyat = np.poly1d(z)(v_yil) * 1.06 # %6 hatasızlık payı ekle
            emsal_notu = "Model yılında veri olmadığı için genel pazar trendi (hatasız bazda) hesaplandı."

        # --- DÜZELTMELER ---
        vites_farki = 65000 if v_vites == "Otomatik" else -20000
        tramer_kesintisi = v_hasar * 0.15 # Tramerin %15'i
        
        # Parça başı düşüşler (Hatasız bazdan düşüyoruz)
        kritik = ["Tavan", "Kaput", "Bagaj Kapağı"]
        boya_dususu = sum([15000 if p in kritik else 8000 for p in v_boya])
        degisen_dususu = sum([35000 if p in kritik else 20000 for p in v_degisen])
        
        final_price = hatasiz_baz_fiyat + vites_farki - (tramer_kesintisi + boya_dususu + degisen_dususu)

        # --- SONUÇ ---
        st.markdown(f"""
            <div class='price-box'>
                <p style='color:#000; font-weight:700; opacity:0.6;'>HATASIZ EMSAL ÜSTÜNDEN DEĞERLEME</p>
                <h1 class='price-val'>{max(0, final_price):,.0f} TL</h1>
                <p style='margin:0; font-size:0.85rem; color:#444;'>{emsal_notu}</p>
            </div>
        """, unsafe_allow_html=True)

        # --- REFERANS ALINAN HATASIZ ARAÇLAR ---
        if not yil_daslar.empty:
            st.markdown("### 🔍 Baz Alınan En Temiz Emsaller")
            for _, row in hatasiz_emsaller.iterrows():
                st.markdown(f"""
                    <div class='emsal-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <span style='color:#FFF;'>{row['Yıl']} Model • {row['KM']:,.0f} KM</span>
                            <span style='color:#FFCC00; font-weight:800;'>{row['Fiyat']:,.0f} TL</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    if st.button("🔄 SIFIRLA"):
        del st.session_state.data
        st.rerun()
