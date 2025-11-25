import sqlite3

from config.constants import DB_NAME


def setup_db_files() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.cursor().execute("DROP TABLE IF EXISTS files")
    conn.cursor().execute(
        "CREATE TABLE files(filename, error, missing, status, cert_id, name, year_from)"
    )
    conn.commit()
    return conn


def setup_db_fips_versions(name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(name)
    conn.cursor().execute("DROP TABLE IF EXISTS fips_version")
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS fips_version(filename, version)")
    conn.commit()
    return conn


def insert_file_metadata(
    file_name: str, error: int, missing: int, row, db_cur: sqlite3.Cursor
):
    db_cur.execute(
        """INSERT INTO files VALUES(?, ?, ?, ?, ?, ?, ?)""",
        (
            file_name,
            error,
            missing,
            row["status"],
            row["cert_id"],
            row["name"],
            row["year_from"],
        ),
    )


def insert_fips_version(file_name: str, version: str, db_cur: sqlite3.Cursor):
    db_cur.execute("""INSERT INTO fips_version VALUES(?, ?)""", (file_name, version))
