import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Konfigurasi Halaman (Auto / Centered agar bagus di HP)
st.set_page_config(
    page_title="Form Inspeksi Truk - PT PJPT Senopati",
    page_icon="🚛",
    layout="centered",  # Optimal untuk tampilan HP / Layar Tegak
    initial_sidebar_state="collapsed"  # Sidebar otomatis tersembunyi di HP
)

# Custom CSS khusus HP (Memperbesar tombol, teks, dan padding)
st.markdown("""
    <style>
    /* Mengatur padding atas agar pas di layar HP */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    /* Memperbesar ukuran teks label radio/pilihan */
    div[class*="stRadio"] label {
        font-size: 16px !important;
        font-weight: 500;
    }
    /* Tombol Submit Besar & Jelas */
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

# Inisialisasi Session State
if "data_inspeksi" not in st.session_state:
    st.session_state["data_inspeksi"] = [
        {
            "Waktu Input": "2026-08-22 07:30",
            "Tanggal": "2026-08-22",
            "No. Polisi": "B 9001 PT",
            "Driver": "Siti",
            "KM Awal": 125000,
            "Status Kelayakan": "SIAP OPERASIONAL (Kondisi Baik)",
            "Catatan Kendala": "-"
        }
    ]

# Navigation
menu = st.sidebar.radio("Pilih Halaman:", ["Form Inspeksi (Driver)", "Dashboard Maintenance (Admin)"])

# ====================================================
# 1. FORM INSPEKSI DRIVER (MOBILE OPTIMIZED)
# ====================================================
if menu == "Form Inspeksi (Driver)":
    st.title("🚛 Form Inspeksi Harian Truk")
    st.caption("PT PJPT Senopati - Fleet Maintenance")
    st.info("💡 **Petunjuk Driver:** Isi form ceklist ini secara teliti sebelum memulai perjalanan.")

    with st.form("form_inspeksi_mobile"):
        st.subheader("📌 1. Data Driver & Kendaraan")
        
        nama_driver = st.text_input("Nama Driver", placeholder="Masukkan nama Anda...")
        no_polisi = st.selectbox("Nomor Polisi Truk", ["B 9001 PT", "B 9002 PT", "B 9003 PT", "B 9004 PT"])
        km_awal = st.number_input("Odometer / KM Awal", min_value=0, step=100)
        tgl_inspeksi = st.date_input("Tanggal Inspeksi", datetime.now())

        st.write("---")
        st.subheader("🔧 2. Ceklist Kondisi Komponen")

        # Pilihan disusun vertikal (mudah di-tap jempol di HP)
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
                
                data_baru = {
                    "Waktu Input": waktu_sekarang,
                    "Tanggal": str(tgl_inspeksi),
                    "No. Polisi": no_polisi,
                    "Driver": nama_driver,
                    "KM Awal": km_awal,
                    "Status Kelayakan": status_layak,
                    "Catatan Kendala": catatan if catatan.strip() else "-"
                }
                
                st.session_state["data_inspeksi"].append(data_baru)
                st.session_state["inspeksi_terakhir"] = data_baru
                st.session_state["detail_terakhir"] = {
                    "Oli Mesin": oli, "Air Radiator": radiator, "Minyak Rem": minyak_rem,
                    "Kondisi Ban": ban, "Baut Roda": baut_roda, "Rem Utama": rem,
                    "Lampu-Lampu": lampu, "Wiper & Klakson": wiper_klakson,
                    "STNK & KIR": dokumen, "Tools & Segitiga": tools
                }

                st.balloons()
                st.success("✅ Laporan Berhasil Terkirim!")

    # BUKTI RINGKASAN UNTUK DRIVER
    if "inspeksi_terakhir" in st.session_state:
        st.write("---")
        st.subheader("📄 Bukti Laporan Inspeksi Driver")
        
        data_tampil = st.session_state["inspeksi_terakhir"]
        detail_tampil = st.session_state["detail_terakhir"]

        if "SIAP OPERASIONAL" in data_tampil["Status Kelayakan"]:
            st.success(f"✅ **{data_tampil['Status Kelayakan']}**")
        else:
            st.error(f"⚠️ **{data_tampil['Status Kelayakan']}**")

        st.write(f"**Driver:** {data_tampil['Driver']}")
        st.write(f"**Nopol Truk:** {data_tampil['No. Polisi']}")
        st.write(f"**Odometer:** {data_tampil['KM Awal']:,} KM")
        st.write(f"**Waktu:** {data_tampil['Waktu Input']}")
        st.write(f"**Catatan:** {data_tampil['Catatan Kendala']}")

        st.markdown("**Detail Pengecekan:**")
        df_detail = pd.DataFrame(list(detail_tampil.items()), columns=["Komponen", "Kondisi"])
        df_detail.index = range(1, len(df_detail) + 1)
        
        # DataFrame responsif di HP
        st.dataframe(df_detail, use_container_width=True)

# ====================================================
# 2. DASHBOARD ADMIN MAINTENANCE
# ====================================================
elif menu == "Dashboard Maintenance (Admin)":
    st.title("📊 Dashboard Admin Fleet")
    st.caption("Rekapitulasi Kesiapan Truk PT PJPT Senopati")
    st.write("---")

    df_admin = pd.DataFrame(st.session_state["data_inspeksi"])
    df_admin.index = range(1, len(df_admin) + 1)

    total = len(df_admin)
    layak = len(df_admin[df_admin["Status Kelayakan"].str.contains("SIAP OPERASIONAL")])
    perbaikan = total - layak

    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Total Laporan", f"{total}")
    col_m2.metric("Perlu Action", f"{perbaikan}")

    st.write("---")
    st.subheader("Data Inspeksi Masuk")
    st.dataframe(df_admin, use_container_width=True)