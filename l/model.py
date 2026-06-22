# model.py
import datetime

class KamarKos:
    def __init__(self, nomor_kamar: str, nama_penghuni: str, kontak: str, kontak_darurat: str, status: str):
        self.nomor_kamar = nomor_kamar
        self.nama_penghuni = nama_penghuni
        self.kontak = kontak
        self.kontak_darurat = kontak_darurat
        self.status = status

class PembayaranKos:
    def __init__(self, kamar: str, bulan: str, tahun: int, jumlah: float, tanggal: datetime.date, keterangan: str = "Lunas", id_bayar=None):
        self.id = id_bayar
        self.kamar = kamar
        self.bulan = bulan
        self.tahun = tahun
        self.jumlah = jumlah
        self.tanggal = tanggal
        self.keterangan = keterangan