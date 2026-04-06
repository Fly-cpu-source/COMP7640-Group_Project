"""
product.py — Product DAO for ReMarket.
Functional Point ②: Browse products by vendor / Add product.
Functional Point ③: Search by tag (fuzzy LIKE matching).
"""
from db import get_connection


def get_products_by_vendor(vendor_id):
    """Return all products belonging to the given vendor."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM Product WHERE vendor_id = %s ORDER BY product_id",
                (vendor_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()


def search_by_tag(keyword):
    """
    Fuzzy search: return products whose name OR tags contain the keyword.
    Uses SQL LIKE with % wildcards — NOT exact matching.
    """
    conn = get_connection()
    pattern = f"%{keyword}%"
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.*, v.business_name AS vendor_name
                FROM Product p
                JOIN Vendor v ON p.vendor_id = v.vendor_id
                WHERE p.product_name LIKE %s OR p.tags LIKE %s
                ORDER BY p.product_id
                """,
                (pattern, pattern),
            )
            return cur.fetchall()
    finally:
        conn.close()


def add_product(vendor_id, product_name, price, stock_quantity, tags):
    """Insert a new product for the given vendor and return the new product_id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Product (product_name, price, stock_quantity, tags, vendor_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (product_name, price, stock_quantity, tags, vendor_id),
            )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_product_by_id(product_id):
    """Return a single product dict or None if not found."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Product WHERE product_id = %s", (product_id,))
            return cur.fetchone()
    finally:
        conn.close()
