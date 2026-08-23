import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ====================================================
# 1. KONFIGURASI HALAMAN
# ====================================================
st.set_page_config(
    page_title="Form Inspeksi Truk - PT PJPT Senopati",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL WEBHOOK APPS SCRIPT ANDA:
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwM4DKHZBzGaQ7OIxFgBUnxuftBUWRRR2HySjKV6QUVqp4v9SaR_kdfYOHRRL1eg8gXdA/exec"

# Custom CSS untuk kerapatan layout dan sidebar
st.markdown("""
    <style>
    /* 1. Potong padding area utama */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* 2. Paksa HAPUS padding bawaan Streamlit di Sidebar */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem !important;
    }
    [data-testid="stSidebarContent"] {
        padding-top: 0rem !important;
    }
    
    /* 3. Rapikan margin heading di sidebar */
    [data-testid="stSidebar"] h1 {
        margin-top: -10px !important;
        padding-top: 0px !important;
    }
    
    div[class*="stRadio"] label {
        font-size: 16px !important;
        font-weight: 500;
    }
    div.stButton > button:first-child {
        width: 100%;
        background-color: #0066cc;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 12px;
        border-radius: 10px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# ====================================================
# 2. SIDEBAR NAVIGASI
# ====================================================
st.sidebar.markdown("# **🚚 DASHBOARD**")
st.sidebar.caption("**PT PJPT Senopati Fleet System**")
st.sidebar.write("---")

st.sidebar.subheader("Pilih Halaman:")
menu = st.sidebar.radio(
    "",
    ["Form Inspeksi (Driver)", "Dashboard Maintenance (Admin)"]
)
st.sidebar.write("---")

# ====================================================
# 3. KONEKSI & PEMBACAAN GOOGLE SHEETS FOR FORM
# ====================================================
conn = st.connection("gsheets", type=GSheetsConnection)

dict_truk = {}
err_msg = ""

# --- BACA DATA MASTER TRUK ---
try:
    try:
        df_truk = conn.read(worksheet="Master_Truk", ttl="1m")
    except Exception:
        df_truk = conn.read(ttl="1m")
    
    col_nopol = next((c for c in df_truk.columns if "polisi" in str(c).lower() or "nopol" in str(c).lower()), None)
    col_type = next((c for c in df_truk.columns if "jenis" in str(c).lower() or "type" in str(c).lower() or "merk" in str(c).lower()), None)

    if col_nopol:
        df_clean = df_truk.dropna(subset=[col_nopol]).drop_duplicates(subset=[col_nopol])
        for _, row in df_clean.iterrows():
            nopol_val = str(row[col_nopol]).strip()
            type_val = str(row[col_type]).strip() if col_type and pd.notna(row[col_type]) else "-"
            dict_truk[nopol_val] = type_val
    else:
        err_msg = f"Kolom No Polisi tidak terdeteksi. Kolom yang dibaca: {list(df_truk.columns)}"

except Exception as e:
    err_msg = f"Gagal membaca Master Truk: {str(e)}"

# Fallback jika master truk gagal dibaca
if not dict_truk:
    dict_truk = {
        "B 9688 YU": "MITSUBISHI CANTER",
        "B 9693 YU": "CANTER BOX",
        "B 9679 YU": "ENGKEL"
    }

daftar_nopol_only = list(dict_truk.keys())


# ====================================================
# 4. HALAMAN 1: FORM INSPEKSI DRIVER
# ====================================================
if menu == "Form Inspeksi (Driver)":
    st.title("🚛 Form Inspeksi Harian Truk")
    st.caption("PT PJPT Senopati - Fleet Maintenance")
    
    if err_msg:
        st.warning(f"⚠️ Warning Koneksi Master Data:\n{err_msg}")
    else:
        st.info("💡 **Petunjuk Driver:** Isi form ceklist ini secara teliti sebelum memulai perjalanan.")

    st.subheader("📌 1. Data Driver & Kendaraan")
    
    # Input Nama Driver
    nama_driver = st.text_input("Nama Driver", placeholder="Masukkan nama Anda...")
    
    # Selectbox Nopol (Reaktif secara Real-Time)
    no_polisi = st.selectbox("Nomor Polisi Truk", daftar_nopol_only)
    
    # Mengambil Jenis Kendaraan secara otomatis berdasarkan Nopol
    jenis_otomatis = dict_truk.get(no_polisi, "-")
    
    # Field Jenis Kendaraan terisi otomatis & terkunci
    st.text_input("Jenis Kendaraan", value=jenis_otomatis, disabled=True)

    # Form Inspeksi Utama
    with st.form("form_inspeksi_mobile"):
        km_awal = st.number_input("Odometer / KM Awal", min_value=0, step=100)
        tgl_inspeksi = st.date_input("Tanggal Inspeksi", datetime.now())

        st.write("---")
        st.subheader("🔧 2. Ceklist Kondisi Komponen")

        st.markdown("--- **A. Mesin & Cairan** ---")
        oli = st.radio("1. Oli Mesin", ["Baik / Cukup", "Kurang", "Bocor"], index=0)
        radiator = st.radio("2. Air Radiator", ["Baik / Cukup", "Kurang"], index=0)
        minyak_rem = st.radio("3. Minyak Rem & Kopling", ["Baik / Cukup", "Kurang"], index=0)

        st.markdown("--- **B. Ban & Rem** ---")
        ban = st.radio("4. Kondisi & Tekanan Ban", ["Baik", "Gundul / Kurang Angin"], index=0)
        baut_roda = st.radio("5. Baut Roda", ["Kencang & Lengkap", "Ada Kendur / Lolos"], index=0)
        rem = st.radio("6. Rem Utama & Handbrake", ["Pakem / Normal", "Blong / Kurang Pakem"], index=0)

        st.markdown("--- **C. Kelistrikan & Lampu** ---")
        lampu = st.radio("7. Lampu Depan, Sein & Rem", ["Berfungsi Semua", "Ada yang Mati"], index=0)
        wiper_klakson = st.radio("8. Wiper & Klakson", ["Berfungsi Baik", "Rusak / Mati"], index=0)

        st.markdown("--- **D. Dokumen & Tools** ---")
        dokumen = st.radio("9. STNK & Kartu KIR", ["Lengkap & Berlaku", "Tidak Ada / Kadaluarsa"], index=0)
        tools = st.radio("10. Dongkrak & Segitiga", ["Tersedia / Ada", "Tidak Ada"], index=0)

        st.write("---")
        st.subheader("📝 3. Kesimpulan Akhir")
        
        status_layak = st.selectbox(
            "Status Kesiapan Armada:",
            [
                "SIAP OPERASIONAL (Kondisi Baik)",
                "PERLU PERBAIKAN SEGERA (Tidak Layak Jalan)"
            ]
        )
        catatan = st.text_area("Catatan Kendala (Kosongkan jika normal):", placeholder="Contoh: Lampu sein kiri mati...")

        st.write("")
        submit_button = st.form_submit_button(label="🚀 KIRIM LAPORAN INSPEKSI")

        if submit_button:
            if not nama_driver.strip():
                st.error("⚠️ Nama Driver wajib diisi!")
            else:
                waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Payload JSON ke Webhook Apps Script
                payload = {
                    "waktu": waktu_sekarang,
                    "tanggal": str(tgl_inspeksi),
                    "nopol": no_polisi,
                    "jenis": jenis_otomatis,
                    "driver": nama_driver,
                    "km": km_awal,
                    "status": status_layak,
                    "catatan": catatan if catatan.strip() else "-"
                }
                
                # Kirim data
                try:
                    res = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
                    if res.status_code == 200:
                        st.success("✅ Laporan Berhasil Terkirim & Tersimpan di Database Google Sheets!")
                        st.balloons()
                    else:
                        st.error(f"Gagal mengirim data. Kode Respon: {res.status_code}")
                except Exception as e:
                    st.error(f"Terjadi kesalahan koneksi ke Apps Script: {e}")

                st.session_state["detail_terakhir"] = {
                    "Oli Mesin": oli, "Air Radiator": radiator, "Minyak Rem": minyak_rem,
                    "Kondisi Ban": ban, "Baut Roda": baut_roda, "Rem Utama": rem,
                    "Lampu-Lampu": lampu, "Wiper & Klakson": wiper_klakson,
                    "STNK & KIR": dokumen, "Tools & Segitiga": tools
                }

    if "detail_terakhir" in st.session_state:
        st.write("---")
        st.subheader("📄 Bukti Laporan Terakhir")
        detail_tampil = st.session_state["detail_terakhir"]

        df_detail = pd.DataFrame(list(detail_tampil.items()), columns=["Komponen", "Kondisi"])
        df_detail.index = range(1, len(df_detail) + 1)
        st.dataframe(df_detail, use_container_width=True)


# ====================================================
# 5. HALAMAN 2: DASHBOARD ADMIN MAINTENANCE
# ====================================================
elif menu == "Dashboard Maintenance (Admin)":
    st.title("📊 Dashboard Admin Fleet")
    st.caption("Rekapitulasi Real-Time PT PJPT Senopati")
    st.write("---")

    if st.button("🔄 Refresh Data"):
        st.rerun()

    # Link Spreadsheet & GID Tab Data Inspeksi
    SHEET_ID = "1tRosUe7LHcyWrpKC2nhO6RWKkvcWqym7AKNdliuLp98"
    GID_TAB = "1078542922"
    
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_TAB}"

    try:
        df_inspeksi = pd.read_csv(csv_url)

        if not df_inspeksi.empty:
            st.subheader("📌 Ringkasan Armada")
            
            total = len(df_inspeksi)
            
            # Deteksi kolom status (Kolom ke-6 / indeks ke-5)
            col_status = df_inspeksi.columns[5] if len(df_inspeksi.columns) >= 6 else df_inspeksi.columns[-1]
            
            layak = len(df_inspeksi[df_inspeksi[col_status].astype(str).str.contains("SIAP OPERASIONAL", na=False)])
            perbaikan = total - layak

            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Total Laporan Masuk", f"{total}")
            col_m2.metric("Perlu Action / Perbaikan", f"{perbaikan}")

            st.write("---")
            st.subheader("📄 Data Laporan Inspeksi Masuk")
            st.dataframe(df_inspeksi, use_container_width=True)
        else:
            st.info("Belum ada data di sheet Data_Inspeksi.")

    except Exception as e:
        st.error(f"Gagal memuat data dari Google Sheets: {e}")