# konfigurasi.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAMA_DB = 'monitoring_kos.db'
DB_PATH = os.path.join(BASE_DIR, NAMA_DB)

BULAN_CHOICES = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]