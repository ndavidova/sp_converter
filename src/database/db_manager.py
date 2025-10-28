from sec_certs.dataset.fips import FIPSDataset
from txt_parsing.mapper import extract_chapters_from_text
import sqlite3
from pathlib import Path

def setup_db_files(name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(name)
    conn.cursor().execute("DROP TABLE files")
    conn.cursor().execute("CREATE TABLE files(filename, error, missing, status, cert_id, name, year_from)")
    conn.commit()
    return conn


def insert_file_metadata(file_name: str, error: int, missing: int, row, db_cur: sqlite3.Cursor):
        db_cur.execute("""INSERT INTO files VALUES(?, ?, ?, ?, ?, ?, ?)""",
            (file_name,
            error, 
            missing,
            row['status'],
            row['cert_id'],
            row['name'],
            row['year_from']))