# database.py
import sqlite3
import pandas as pd
from konfigurasi import DB_PATH

def get_db_connection() -> sqlite3.Connection | None:
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error Koneksi DB: {e}")
        return None

def setup_database_initial():
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # Tabel Kamar & Profil Detail (Tabel Master)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS kamar (
            nomor_kamar TEXT PRIMARY KEY,
            nama_penghuni TEXT NOT NULL,
            kontak TEXT NOT NULL,
            kontak_darurat TEXT NOT NULL,
            status TEXT NOT NULL
        );""")
        
        # Tabel Catatan Pembayaran Bulanan dengan Relasi Foreign Key
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pembayaran (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor_kamar TEXT NOT NULL,
            bulan TEXT NOT NULL,
            tahun INTEGER NOT NULL,
            jumlah REAL NOT NULL,
            tanggal_bayar DATE NOT NULL,
            keterangan TEXT NOT NULL,
            UNIQUE(nomor_kamar, bulan, tahun),
            FOREIGN KEY (nomor_kamar) REFERENCES kamar(nomor_kamar) ON DELETE CASCADE
        );""")
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error setup tabel: {e}")
        return False
    finally:
        if conn: conn.close()

def execute_query(query: str, params: tuple = None):
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        if params: cursor.execute(query, params)
        else: cursor.execute(query)
        conn.commit()
        return cursor.lastrowid if cursor.lastrowid else True
    except sqlite3.Error as e:
        print(f"Error Execute: {e}")
        conn.rollback()
        return None
    finally:
        if conn: conn.close()

def get_dataframe(query: str, params: tuple = None) -> pd.DataFrame:
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    try:
        return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        print(f"Error Pandas DB: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()