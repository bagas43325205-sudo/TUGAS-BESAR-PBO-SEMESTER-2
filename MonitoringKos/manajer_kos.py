import datetime
import pandas as pd
import database
from model import KamarKos, PembayaranKos

class ManajerKos:
    _db_setup_done = False

    def __init__(self):
        if not ManajerKos._db_setup_done:
            database.setup_database_initial()
            ManajerKos._db_setup_done = True

    def tambah_kamar(self, kamar: KamarKos) -> bool:
        sql = """INSERT INTO kamar (nomor_kamar, nama_penghuni, kontak, kontak_darurat, status)
                 VALUES (?, ?, ?, ?, ?)
                 ON CONFLICT(nomor_kamar) DO UPDATE SET
                    nama_penghuni=excluded.nama_penghuni,
                    kontak=excluded.kontak,
                    kontak_darurat=excluded.kontak_darurat,
                    status=excluded.status"""
        params = (kamar.nomor_kamar, kamar.nama_penghuni, kamar.kontak, kamar.kontak_darurat, kamar.status)
        return database.execute_query(sql, params) is not None

    def get_daftar_nomor_kamar(self) -> list:
        df = database.get_dataframe("SELECT nomor_kamar FROM kamar ORDER BY nomor_kamar ASC")
        if df.empty: return []
        return df['nomor_kamar'].tolist()

    def get_semua_kamar_df(self) -> pd.DataFrame:
        return database.get_dataframe("SELECT nomor_kamar, nama_penghuni, kontak, kontak_darurat, status FROM kamar ORDER BY nomor_kamar ASC")

    def hapus_kamar(self, nomor_kamar: str) -> bool:
        sql = "DELETE FROM kamar WHERE nomor_kamar = ?"
        return database.execute_query(sql, (nomor_kamar,)) is not None

    def tambah_pembayaran(self, bayar: PembayaranKos) -> bool:
        sql = """INSERT INTO pembayaran (nomor_kamar, bulan, tahun, jumlah, tanggal_bayar, keterangan) 
                 VALUES (?, ?, ?, ?, ?, ?)"""
        params = (bayar.kamar, bayar.bulan, bayar.tahun, bayar.jumlah, bayar.tanggal, bayar.keterangan)
        last_id = database.execute_query(sql, params)
        if last_id:
            bayar.id = last_id
            return True
        return False

    def get_status_pembayaran(self, bulan: str, tahun: int):
        # Ditambahkan filter AND p.keterangan = 'Lunas'
        # agar DP dan Nyicil otomatis terbaca sebagai Belum Bayar
        query_sudah = """
            SELECT p.nomor_kamar, k.nama_penghuni, p.jumlah, p.tanggal_bayar, p.keterangan 
            FROM pembayaran p
            JOIN kamar k ON p.nomor_kamar = k.nomor_kamar
            WHERE p.bulan = ? AND p.tahun = ? AND p.keterangan = 'Lunas'
        """
        df_sudah = database.get_dataframe(query_sudah, params=(bulan, tahun))
        
        daftar_kamar_all = self.get_daftar_nomor_kamar()
        
        if not df_sudah.empty:
            kamar_sudah = df_sudah['nomor_kamar'].tolist()
        else:
            kamar_sudah = []
            df_sudah = pd.DataFrame(columns=['nomor_kamar', 'nama_penghuni', 'jumlah', 'tanggal_bayar', 'keterangan'])
            
        kamar_belum = [k for k in daftar_kamar_all if k not in kamar_sudah]
        
        if kamar_belum:
            placeholders = ','.join(['?'] * len(kamar_belum))
            query_belum = f"SELECT nomor_kamar, nama_penghuni, kontak, status FROM kamar WHERE nomor_kamar IN ({placeholders})"
            df_belum = database.get_dataframe(query_belum, params=tuple(kamar_belum))
        else:
            df_belum = pd.DataFrame(columns=['nomor_kamar', 'nama_penghuni', 'kontak', 'status'])
        
        return df_sudah, df_belum

    def get_riwayat_pembayaran(self) -> pd.DataFrame:
        query = """
            SELECT p.id, k.nomor_kamar, k.nama_penghuni, p.bulan, p.tahun, p.jumlah, p.tanggal_bayar, p.keterangan
            FROM pembayaran p
            JOIN kamar k ON p.nomor_kamar = k.nomor_kamar
            ORDER BY p.tanggal_bayar DESC, p.id DESC
        """
        return database.get_dataframe(query)

    def hapus_pembayaran(self, id_bayar: int) -> bool:
        sql = "DELETE FROM pembayaran WHERE id = ?"
        return database.execute_query(sql, (id_bayar,)) is not None