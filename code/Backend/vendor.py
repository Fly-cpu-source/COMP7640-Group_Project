"""
vendor.py — Vendor DAO for ReMarket.
Functional Point ①: List all vendors / Add new vendor.
"""
from db import get_connection


def list_vendors():
    """Return a list of all vendors."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Vendor ORDER BY vendor_id")
            return cur.fetchall()
    finally:
        conn.close()


def add_vendor(business_name, geographical_presence):
    """
    Insert a new vendor and return the new vendor_id.
    average_rating starts at 0.00 by default.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Vendor (business_name, geographical_presence) VALUES (%s, %s)",
                (business_name, geographical_presence),
            )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_vendor_by_id(vendor_id):
    """Return a single vendor dict or None if not found."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Vendor WHERE vendor_id = %s", (vendor_id,))
            return cur.fetchone()
    finally:
        conn.close()
