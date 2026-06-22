import streamlit as st
import datetime
import locale
import pandas as pd
import time

try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except:
    pass

from model import KamarKos, PembayaranKos
from manajer_kos import ManajerKos
from konfigurasi import BULAN_CHOICES

st.set_page_config(page_title="Tubes Monitoring Kos", layout="wide")

@st.cache_resource
def get_manajer():
    return ManajerKos()

manajer = get_manajer()

def format_rp(angka):
    try:
        return locale.currency(angka or 0, grouping=True, symbol='Rp ')[:-3]
    except:
        return f"Rp {angka or 0:,.0f}".replace(",",".")

def halaman_kelola_kamar():
    st.header("🏠 Kelola Kamar & Penghuni")
    
    tab1, tab2 = st.tabs(["➕ Tambah / Edit Kamar", "👥 Detail Penghuni"])
    
    with tab1:
        st.subheader("Registrasi Kamar atau Perubahan Data Profil")
        with st.form("form_kamar", clear_on_submit=True):
            nomor_kamar = st.text_input("Nomor Kamar:", placeholder="Contoh: Kamar 01 / Kamar 2A")
            nama_penghuni = st.text_input("Nama Lengkap Penghuni:")
            kontak = st.text_input("Nomor WhatsApp / HP:")
            kontak_darurat = st.text_input("Kontak Darurat:")
            status = st.selectbox("Status :", ["Mahasiswa", "Karyawan", "Wiraswasta", "Lainnya"])
            
            submitted = st.form_submit_button("Simpan Data")
            if submitted:
                if not nomor_kamar.strip() or not nama_penghuni.strip():
                    st.error("Gagal simpan! Nomor kamar dan Nama Penghuni tidak boleh kosong.")
                    st.toast("Data belum lengkap!", icon="⚠️")
                else:
                    kamar_obj = KamarKos(nomor_kamar.strip(), nama_penghuni.strip(), kontak.strip(), kontak_darurat.strip(), status)
                    
                    if manajer.tambah_kamar(kamar_obj):
                        # Jika BERHASIL
                        st.success(f"Data {nomor_kamar} berhasil terekam ke sistem!")
                        st.toast(f"Data kamar {nomor_kamar} berhasil disimpan!", icon="✅")
                        
                        time.sleep(2) # Jeda singkat agar user bisa membaca pesan
                        st.cache_data.clear()
                        st.rerun() # Refresh halaman untuk update tabel
                    else:
                        # Jika GAGAL (muncul error dan toast, tapi TIDAK di-rerun)
                        st.error("Terjadi kesalahan sistem saat menyimpan data ke database.")
                        st.toast("Gagal menyimpan data ke database!", icon="❌")


    with tab2:
        st.subheader("Data Kamar Terdaftar & Kontak Darurat")
        df_kamar = manajer.get_semua_kamar_df()
        if df_kamar.empty:
            st.info("Belum ada unit kamar yang didaftarkan.")
        else:
            df_display = df_kamar.rename(columns={
                'nomor_kamar': 'No. Kamar',
                'nama_penghuni': 'Nama Penghuni',
                'kontak': 'No. Handphone',
                'kontak_darurat': 'Kontak Darurat',
                'status': 'Status Penghuni'
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("🗑️ Hapus Unit")
            kamar_hapus = st.selectbox("Pilih Kamar yang Akan Dihapus:", manajer.get_daftar_nomor_kamar())
            if st.button("Hapus Kamar", type="primary"):
                if manajer.hapus_kamar(kamar_hapus):
                    st.success(f"Kamar {kamar_hapus} berhasil dibersihkan dari database.")
                    st.cache_data.clear()
                    st.rerun()

def halaman_input_pembayaran():
    st.header("📝 Catat Pembayaran Kos")
    daftar_kamar_aktif = manajer.get_daftar_nomor_kamar()
    
    if not daftar_kamar_aktif:
        st.warning("Peringatan: Silakan daftarkan kamar terlebih dahulu di menu 'Kelola Kamar & Penghuni'.")
        return

    with st.form("form_bayar", clear_on_submit=True):
        kamar = st.selectbox("Nomor Kamar Tujuan*:", daftar_kamar_aktif)
        
        bulan_pilihan = st.multiselect("Bulan Tagihan (Bisa pilih lebih dari satu)*:", BULAN_CHOICES, default=[BULAN_CHOICES[datetime.date.today().month - 1]])
        tahun = st.number_input("Tahun Tagihan*:", min_value=2000, max_value=2100, value=datetime.date.today().year)
        
        jumlah_total = st.number_input("Total Nominal Transaksi (Rp)*:", min_value=0, step=50000, value=500000)
        
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Setor*:", value=datetime.date.today())
        with col2:
            # Mengubah list pilihan status pembayaran
            keterangan = st.selectbox("Status Pembayaran*:", ["Lunas", "DP", "Nyicil"])
            
        submitted = st.form_submit_button("Simpan Pembayaran")
        
        if submitted:
            if not bulan_pilihan:
                st.error("Minimal pilih 1 bulan tagihan!")
            else:
                jumlah_per_bulan = float(jumlah_total) / len(bulan_pilihan)
                sukses = 0
                gagal = 0
                
                for b in bulan_pilihan:
                    bayar = PembayaranKos(kamar, b, tahun, jumlah_per_bulan, tanggal, keterangan)
                    if manajer.tambah_pembayaran(bayar):
                        sukses += 1
                    else:
                        gagal += 1
                
                if sukses > 0:
                    st.success(f"Berhasil menyimpan {sukses} data pembayaran untuk kamar {kamar}!")
                if gagal > 0:
                    st.warning(f"Gagal menyimpan {gagal} bulan (kemungkinan data bulan tersebut sudah diinput sebelumnya).")
                st.cache_data.clear()

def halaman_status_dashboard():
    st.header("📊 Dashboard Monitoring Real-Time")
    
    tab1, tab2 = st.tabs(["🚦 Status Tagihan Bulanan", "📈 Riwayat & Laporan Keuangan"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            filter_bulan = st.selectbox("Periode Bulan:", BULAN_CHOICES, index=datetime.date.today().month - 1)
        with col2:
            filter_tahun = st.number_input("Periode Tahun:", min_value=2000, max_value=2100, value=datetime.date.today().year)
            
        st.divider()
        
        df_sudah, df_belum = manajer.get_status_pembayaran(filter_bulan, filter_tahun)
        col_sudah, col_belum = st.columns(2)
        
        with col_sudah:
            st.subheader("✅ Lunas")
            if df_sudah.empty:
                st.info("Nihil. Belum ada yang lunas bulan ini.")
            else:
                df_sudah_display = df_sudah.copy()
                df_sudah_display['jumlah'] = df_sudah_display['jumlah'].apply(format_rp)
                df_sudah_display.rename(columns={'nomor_kamar':'Kamar', 'nama_penghuni':'Penghuni', 'jumlah':'Nominal', 'tanggal_bayar':'Tanggal', 'keterangan':'Status'}, inplace=True)
                st.dataframe(df_sudah_display, use_container_width=True, hide_index=True)
                
                # FITUR EXPORT LAPORAN
                csv = df_sudah_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Laporan Lunas (CSV)",
                    data=csv,
                    file_name=f"Laporan_Lunas_{filter_bulan}_{filter_tahun}.csv",
                    mime="text/csv"
                )
                
        with col_belum:
            st.subheader("❌ Belum Lunas (Nyicil / DP)")
            if df_belum.empty:
                st.success("Sempurna! Semua kamar lunas tanpa tunggakan.")
            else:
                df_belum_display = df_belum.rename(columns={'nomor_kamar': 'Kamar', 'nama_penghuni': 'Nama Penghuni', 'kontak': 'No. HP', 'status': 'Status Penghuni'})
                st.dataframe(df_belum_display, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Grafik Total Pendapatan Kos")
        df_riwayat = manajer.get_riwayat_pembayaran()
        
        if df_riwayat.empty:
            st.info("Belum ada data transaksi untuk ditampilkan.")
        else:
            df_grafik = df_riwayat.copy()
            df_grafik['Periode'] = df_grafik['bulan'] + " " + df_grafik['tahun'].astype(str)
            pendapatan_per_bulan = df_grafik.groupby('Periode')['jumlah'].sum().reset_index()
            
            st.bar_chart(pendapatan_per_bulan.set_index('Periode')['jumlah'], use_container_width=True)
            
            st.divider()
            st.subheader("Tabel Seluruh Riwayat Transaksi")
            
            df_tabel = df_riwayat.copy()
            df_tabel['jumlah'] = df_tabel['jumlah'].apply(format_rp)
            st.dataframe(df_tabel, use_container_width=True, hide_index=True)
            
            st.caption("Admin salah input nominal? Hapus ID Transaksinya di bawah ini:")
            col_del1, col_del2 = st.columns([1, 2])
            with col_del1:
                id_hapus = st.number_input("Masukkan ID Transaksi:", min_value=1, step=1)
            with col_del2:
                st.write("") 
                st.write("")
                if st.button("🗑️ Hapus Transaksi", type="primary"):
                    if manajer.hapus_pembayaran(id_hapus):
                        st.success(f"Transaksi ID {id_hapus} berhasil dibatalkan!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("ID Transaksi tidak ditemukan atau gagal dihapus.")

def main():
    st.sidebar.title("🖥️ Monitoring Kos")
    menu = st.sidebar.radio ("Pilih Menu:", ["Kelola Kamar & Penghuni", "Tambah Pembayaran", "Status Pembayaran"])
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Pemrograman Berorientasi Objek 2026")
    
    if menu == "Kelola Kamar & Penghuni":
        halaman_kelola_kamar()
    elif menu == "Tambah Pembayaran":
        halaman_input_pembayaran()
    elif menu == "Status Pembayaran":
        halaman_status_dashboard()

if __name__ == "__main__":
    main()