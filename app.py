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
    layout="centered",
    initial_sidebar_state="collapsed"
)

# PASTE URL WEBHOOK APPS SCRIPT ANDA DI SINI:
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwM4DKHZBzGaQ7OIxFgBUnxuftBUWRRR2HySjKV6QUVqp4v9SaR_kdfYOHRRL1eg8gXdA/exec"

# Custom CSS untuk tampilan mobile
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
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
# 2. KONEKSI & PEMBACAAN GOOGLE SHEETS (BACA DATA)
# ====================================================
conn = st.connection("gsheets", type=GSheetsConnection)

daftar_nopol = []
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
        if col_type:
            daftar_nopol = (df_clean[col_nopol].astype(str) + " (" + df_clean[col_type].astype(str) + ")").tolist()
        else:
            daftar_nopol = df_clean[col_nopol].astype(str).tolist()
    else:
        err_msg = f"Kolom No Polisi tidak terdeteksi. Kolom yang dibaca: {list(df_truk.columns)}"

except Exception as e:
    err_msg = f"Gagal membaca Master Truk: {str(e)}"

# Fallback jika master truk gagal dibaca
if not daftar_nopol:
    daftar_nopol = ["B 9688 YU (Canter)", "B 9693 YU (Canter)", "B 9679 YU (Box CD)"]

# --- BACA DATA RIWAYAT INSPEKSI ---
columns_standard = [
    "Waktu Input", "Tanggal", "No. Polisi", "Driver", "KM Awal", "Status Kelayakan", "Catatan Kendala"
]

try:
    df_inspeksi = conn.read(worksheet="Data_Inspeksi", ttl="0s")
    for col in columns_standard:
        if col not in df_inspeksi.columns:
            df_inspeksi[col] = None
except Exception:
    df_inspeksi = pd.DataFrame(columns=columns_standard)

# ====================================================
# 3. MENU NAVIGASI
# ====================================================
menu = st.sidebar.radio("Pilih Halaman:", ["Form Inspeksi (Driver)", "Dashboard Maintenance (Admin)"])

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

    with st.form("form_inspeksi_mobile"):
        st.subheader("📌 1. Data Driver & Kendaraan")
        
        nama_driver = st.text_input("Nama Driver", placeholder="Masukkan nama Anda...")
        no_polisi = st.selectbox("Nomor Polisi Truk", daftar_nopol)
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

    SHEET_ID = "1g3w4OAozWIUnOxXCZ8aAS-YbiA6OeV68Z40wNw50NHRZj-OqazPTWJXP"
    
    # URL CSV otomatis membaca sheet pertama (gid=0)
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

    try:
        df_inspeksi = pd.read_csv(csv_url)

        if not df_inspeksi.empty:
            st.subheader("📌 Ringkasan Armada")
            
            total = len(df_inspeksi)
            
            # Ambil kolom status (kolom ke-6 / Indeks 5)
            col_status = df_inspeksi.columns[5] if len(df_inspeksi.columns) >= 6 else df_inspeksi.columns[-2]
            
            layak = len(df_inspeksi[df_inspeksi[col_status].astype(str).str.contains("SIAP OPERASIONAL", na=False)])
            perbaikan = total - layak

            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Total Laporan Masuk", f"{total}")
            col_m2.metric("Perlu Action / Perbaikan", f"{perbaikan}")

            st.write("---")
            st.subheader("📄 Data Laporan Inspeksi Masuk")
            st.dataframe(df_inspeksi, use_container_width=True)
        else:
            st.info("Belum ada data di spreadsheet.")

    except Exception as e:
        st.error(f"Gagal memuat data dari Google Sheets: {e}")