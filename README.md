# TUGAS-BESAR-PBO-SEMESTER-2
TUGAS BESAR Mata Kuliah Pemrograman Berorientasi Objek Semester 2
# 🏠 Monitoring Kos: Sistem Manajemen Penghuni & Keuangan Dinamis

Aplikasi pengelolaan kos dan pencatatan transaksi keuangan bulanan berbasis **Web App** yang mengintegrasikan paradigma **Object-Oriented Programming (Python OOP)** dengan **Penyimpanan Relasional (SQLite)** dan **Data Science (Pandas)**. Proyek ini disusun sebagai Tugas Besar mata kuliah Pemrograman Berorientasi Objek 2026.

---

## 🚀 Fitur Utama
* **Dynamic Room Manager**: pendaftaran, pembaruan data profil (*upsert*), dan penghapusan unit kamar kos secara langsung melalui antarmuka web.
* **Bulk Payment Simulation**: mendukung pembayaran rapel (banyak bulan sekaligus). Sistem secara otomatis mengalkulasi pembagian nominal transaksi secara rata per bulan.
* **Real-Time Dashboard Tracking**: pemisahan visual otomatis antara kamar yang berstatus "Lunas" dan kamar yang memiliki tunggakan ("DP/Nyicil") pada periode tertentu.
* **Automated Financial Analytics**: visualisasi data pendapatan riil dari database ke dalam bentuk grafik batang (*Bar Chart*) interaktif.
* **Data Portability (Export CSV)**: fitur unduh laporan data kelunasan hanya dengan satu klik untuk keperluan pembukuan lanjutan di Microsoft Excel.
* **Undo Transaction**: mekanisme pembatalan atau penghapusan riwayat transaksi spesifik berdasarkan ID Transaksi untuk mitigasi *human error*.

---

## 📂 Struktur Arsitektur Proyek
Aplikasi ini menerapkan pemisahan fungsionalitas independen (*Separation of Concerns* / *Modular Design*):

```text
TUBES_PBO/
│
├── konfigurasi.py    # Konfigurasi path database global & master data bulan
├── model.py          # Blueprints / Kelas Entitas (KamarKos & PembayaranKos)
├── database.py       # Lapisan abstraksi database (koneksi, setup tabel, & raw query)
├── manajer_kos.py    # Logika bisnis utama, manipulasi data, & filter transaksional
├── main_app.py       # Representasi antarmuka pengguna (UI) berbasis Streamlit
└── monitoring_kos.db # Berkas basis data relasional SQLite (Dibuat otomatis oleh sistem)
```

## 🧠 Konsep OOP & Fitur Teknis yang Diterapkan
Encapsulation (Enkapsulasi): membungkus data variabel profil penghuni dan properti pembayaran ke dalam objek kelas KamarKos dan PembayaranKos.

Modularity (Modularitas): Isolasi total antara fungsi antarmuka (main_app.py), otak pengontrol (manajer_kos.py), dan akses query database (database.py).

Data Persistence: Mengubah data objek sementara di memori komputer (RAM) menjadi data permanen di dalam harddisk menggunakan SQLite.

Relasi Database (Cascading Delete): Hubungan One-to-Many antara tabel kamar dan pembayaran. Menghapus data induk (kamar) otomatis menyapu bersih seluruh log transaksi anak (pembayaran) demi menjaga integritas data.

## ⚙️ Langkah Instalasi & Urutan Menjalankan Aplikasi
Buka terminal di text editor Anda (misal: VS Code) dan jalankan perintah:

```Bash
pip install streamlit pandas
```

Menjalankan server aplikasi Pastikan direktori terminal berada di dalam folder proyek ini, lalu eksekusi:


```Bash
python -m streamlit run main_app.py
```
(Catatan: Jika Windows mengarahkan ke Microsoft Store, gunakan perintah: ```py -m streamlit run main_app.py```)

## Alur Simulasi Awal (Wajib Diikuti)

1. Buka menu Kelola Kamar & Penghuni terlebih dahulu.

2. Daftarkan 1 atau 2 nomor kamar contoh (misal: Kamar 01).

3. Pindah ke menu Tambah Pembayaran untuk menyimulasikan transaksi keuangan bulanan.

4. Pantau hasilnya secara langsung di menu Status Pembayaran.
