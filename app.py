import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Konfigurasi Halaman
st.set_page_config(
    page_title="Analisis Intertemporal Batubara PT Bukit Asam",
    page_icon=" 煤 ",
    layout="wide",
)

# -----------------------------
# Helper Functions
# -----------------------------
def fmt_idr(value: float) -> str:
    return f"Rp {value:,.2f}"

def fmt_num(value: float) -> str:
    return f"{value:,.2f}"

# -----------------------------
# 1. Inisialisasi Data Historis (Berdasarkan Tabel PDF)
# -----------------------------
# Data diambil dari Tabel Biaya Marginal (MC) Hal. 2
data_dict = {
    "Tahun": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    "Beban_Pokok_Miliar": [30669.75, 29338.56, 24683.50, 15777.29, 1282.24, 14176.46, 12620.83, 10547.43, 9200.73, 9110.15, 9444.15],
    "Produksi_Q": [41900000, 41900000, 37100000, 30000000, 24800000, 29100000, 26400000, 24200000, 19600000, 19300000, 16400000],
    "Harga_P": [1245070, 1030857, 1060161, 1472956, 1696741, 1335481, 997325, 2082617, 4741993, 1875929, 1768058],
    "MC_Aktual": [731975.04, 700204.30, 665323.56, 525909.70, 51703.33, 487163.64, 478061.74, 435844.34, 469425.26, 472028.91, 575862.93]
}
df = pd.DataFrame(data_dict)

# -----------------------------
# 2. Parameter Hasil Praktikum (PDF)
# -----------------------------
a_demand = 36.22151          # Intersep dari P = a - bQ (dalam skala regresi)
b_demand = 0.00000454        # Slope permintaan
mc_praktikum = 508500.25     # Rata-rata MC hasil Goalseek (Hal. 2)
T_star_pdf = 114             # Waktu optimal habis cadangan (Hal. 3)
r_default = 0.0475           # Tingkat diskonto yang digunakan di PDF (Hal. 3)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Identitas Penelitian")
st.sidebar.info("Praktikum Estimasi Fungsi Permintaan & Efisiensi Dinamis Batubara PT Bukit Asam 2014-2024")

st.sidebar.subheader("Parameter Simulasi")
discount_rate = st.sidebar.slider("Tingkat Diskonto (r)", 0.0, 0.15, r_default, 0.0025)
horizon = st.sidebar.slider("Horizon Waktu (T)", 10, 150, T_star_pdf, 1)
mc_sim = st.sidebar.number_input("Biaya Marginal (MC)", value=mc_praktikum)

# -----------------------------
# HEADER
# -----------------------------
st.title("Dashboard Analisis Ekonomi Batubara PT Bukit Asam")
st.markdown("---")

# Row 1: Key Metrics
latest_p = df["Harga_P"].iloc[-1]
latest_q = df["Produksi_Q"].iloc[-1]

m1, m2, m3 = st.columns(3)
m1.metric("Harga Terakhir (2024)", fmt_idr(latest_p))
m2.metric("Produksi Terakhir (2024)", f"{latest_q:,.0f} Unit")
m3.metric("MC Rata-rata", fmt_idr(mc_praktikum))

# -----------------------------
# BAB II: ESTIMASI FUNGSI PERMINTAAN
# -----------------------------
st.header("1. Estimasi Fungsi Permintaan")
st.latex(r"P = 36.22151 - 0.00000454Q")
st.write(f"Berdasarkan hasil regresi, Choke Price diperoleh sebesar **{a_demand}** dan kuantitas maksimum saat harga nol adalah **7,929,515 unit**[cite: 14, 24].")

# Plot Permintaan
q_range = np.linspace(0, 8000000, 100)
p_range = a_demand - (b_demand * q_range)
fig_demand, ax_demand = plt.subplots()
ax_demand.plot(q_range, p_range, label="Kurva Permintaan", color="red")
ax_demand.set_xlabel("Kuantitas (Q)")
ax_demand.set_ylabel("Harga (P)")
ax_demand.axhline(0, color='black', lw=1)
ax_demand.legend()
st.pyplot(fig_demand)

# -----------------------------
# BAB III & V: EFISIENSI DINAMIS (HOTELLING)
# -----------------------------
st.header("2. Alokasi Intertemporal & Hotelling Rule")
st.write(f"Waktu Optimal Habis Cadangan ($T^*$) diestimasi sekitar **{T_star_pdf} tahun**[cite: 28].")

# Simulasi Jalur Harga Hotelling
t_years = np.arange(0, horizon + 1)
# Menggunakan logika MUC_t = MUC_0 * (1+r)^t
muc_0 = 15163.0  # Data awal MUC dari tabel Hal. 2
prices_hotelling = [mc_sim + (muc_0 * (1 + discount_rate)**t) for t in t_years]

fig_h, ax_h = plt.subplots()
ax_h.plot(t_years, prices_hotelling, marker='s', label="Proyeksi Jalur Harga Efisien")
ax_h.set_title("Simulasi Kenaikan Harga Berdasarkan Hotelling Rule")
ax_h.set_xlabel("Tahun ke-n (dari 2025)")
ax_h.set_ylabel("Harga Proyeksi")
ax_h.grid(True, alpha=0.3)
st.pyplot(fig_h)

# -----------------------------
# DATA HISTORIS TABEL
# -----------------------------
st.header("3. Data Historis Produksi & Biaya")
st.dataframe(df.style.format({
    "Beban_Pokok_Miliar": "{:,.2f}",
    "Produksi_Q": "{:,.0f}",
    "Harga_P": "{:,.0f}",
    "MC_Aktual": "{:,.2f}"
}), use_container_width=True)

# -----------------------------
# KESIMPULAN (BAB VIII PDF)
# -----------------------------
st.header("4. Analisis & Kesimpulan")
st.info("""
* **Ketersediaan**: PT Bukit Asam memiliki cadangan batubara mencapai miliaran ton[cite: 36].
* **Keberlanjutan**: Peningkatan produksi yang terlalu cepat dapat mempercepat deplesi sumber daya[cite: 37].
* **Efisiensi**: Strategi ekstraksi harus mempertimbangkan nilai intertemporal agar optimal bagi jangka panjang[cite: 40].
""")

st.caption("Data disesuaikan dengan Laporan Praktikum PT Bukit Asam 2014-2024")