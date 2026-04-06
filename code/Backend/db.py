"""
db.py — Database connection module for ReMarket.
Edit DB_CONFIG below to match your MySQL environment.
"""
import pymysql

DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "123456",   # change to your MySQL password
    "database": "remarket",
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_connection():
    """Return a new PyMySQL connection using DB_CONFIG."""
    return pymysql.connect(**DB_CONFIG)
