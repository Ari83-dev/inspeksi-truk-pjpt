import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Konfigurasi Halaman (Mobile Friendly)
st.set_page_config(
    page_title="Form Inspeksi Truk - PT PJPT Senopati",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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

# 2. Inisialisasi Koneksi Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- BACA MASTER DATA KENDARAAN REAL PT PJPT SENOPATI ---
# Catatan: Sesuaikan nama worksheet jika nama tab di Google Sheets Anda bukan "Master_Truk"
NAMA_TAB_MASTER = "Master_Truk" 

try:
    df_truk = conn.read(worksheet=NAMA_TAB_MASTER, ttl="1m")
    
    # Filter dan ambil kolom No.Polisi dan Type dari Excel asli
    df_truk_clean = df_truk.dropna(subset=["No.Polisi"])
    daftar_nopol = (df_truk_clean["No.Polisi"].astype(str) + " (" + df_truk_clean["Type"].astype(str) + ")").tolist()
except Exception as e:
    # Fallback dummy jika koneksi Google Sheets belum di-setting
    daftar_nopol = ["B 9688 YU (Canter)", "B 9693 YU (Canter)", "B 9679 YU (Box CD)", "B 9426 WO (Tangki Air)"]

# --- BACA DATA RIWAYAT INSPEKSI ---
try:
    df_inspeksi = conn.read(worksheet="Data_Inspeksi", ttl="0s")
except Exception as e:
    df_inspeksi = pd.DataFrame(columns=[
        "Waktu Input", "Tanggal", "No. Polisi", "Driver", "KM Awal", "Status Kelayakan", "Catatan Kendala"
    ])

# Navigation
menu = st.sidebar.radio("Pilih Halaman:", ["Form Inspeksi (Driver)", "Dashboard Maintenance (Admin)"])

# ====================================================
# 1. FORM INSPEKSI DRIVER
# ====================================================
if menu == "Form Inspeksi (Driver)":
    st.title("🚛 Form Inspeksi Harian Truk")
    st.caption("PT PJPT Senopati - Fleet Maintenance")
    st.info("💡 **Petunjuk Driver:** Isi form ceklist ini secara teliti sebelum memulai perjalanan.")

    with st.form("form_inspeksi_mobile"):
        st.subheader("📌 1. Data Driver & Kendaraan")
        
        nama_driver = st.text_input("Nama Driver", placeholder="Masukkan nama Anda...")
        
        # Pilihan Nopol Otomatis Ambil dari Sheet Master PT PJPT
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
                
                data_baru = pd.DataFrame([{
                    "Waktu Input": waktu_sekarang,
                    "Tanggal": str(tgl_inspeksi),
                    "No. Polisi": no_polisi,
                    "Driver": nama_driver,
                    "KM Awal": km_awal,
                    "Status Kelayakan": status_layak,
                    "Catatan Kendala": catatan if catatan.strip() else "-"
                }])
                
                # Simpan ke Google Sheets
                updated_df = pd.concat([df_inspeksi, data_baru], ignore_index=True)
                conn.update(worksheet="Data_Inspeksi", data=updated_df)

                st.session_state["detail_terakhir"] = {
                    "Oli Mesin": oli, "Air Radiator": radiator, "Minyak Rem": minyak_rem,
                    "Kondisi Ban": ban, "Baut Roda": baut_roda, "Rem Utama": rem,
                    "Lampu-Lampu": lampu, "Wiper & Klakson": wiper_klakson,
                    "STNK & KIR": dokumen, "Tools & Segitiga": tools
                }

                st.balloons()
                st.success("✅ Laporan Berhasil Terkirim & Tersimpan di Database Google Sheets!")

    # BUKTI RINGKASAN UNTUK DRIVER
    if "detail_terakhir" in st.session_state:
        st.write("---")
        st.subheader("📄 Bukti Laporan Terakhir")
        detail_tampil = st.session_state["detail_terakhir"]

        df_detail = pd.DataFrame(list(detail_tampil.items()), columns=["Komponen", "Kondisi"])
        df_detail.index = range(1, len(df_detail) + 1)
        st.dataframe(df_detail, use_container_width=True)

# ====================================================
# 2. DASHBOARD ADMIN MAINTENANCE
# ====================================================
elif menu == "Dashboard Maintenance (Admin)":
    st.title("📊 Dashboard Admin Fleet")
    st.caption("Rekapitulasi Real-Time dari Google Sheets PT PJPT Senopati")
    st.write("---")

    if not df_inspeksi.empty:
        total = len(df_inspeksi)
        layak = len(df_inspeksi[df_inspeksi["Status Kelayakan"].str.contains("SIAP OPERASIONAL", na=False)])
        perbaikan = total - layak

        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Total Laporan", f"{total}")
        col_m2.metric("Perlu Action", f"{perbaikan}")

        st.write("---")
        st.subheader("Data Laporan Masuk")
        st.dataframe(df_inspeksi, use_container_width=True)
    else:
        st.info("Belum ada data laporan masuk.")