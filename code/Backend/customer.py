"""
customer.py — Customer DAO for ReMarket.
Supports listing customers and creating new ones at purchase time.
"""
from db import get_connection


def list_customers():
    """Return all customers."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Customer ORDER BY customer_id")
            return cur.fetchall()
    finally:
        conn.close()


def get_customer_by_id(customer_id):
    """Return a customer dict or None if not found."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Customer WHERE customer_id = %s", (customer_id,))
            return cur.fetchone()
    finally:
        conn.close()


def add_customer(contact_number, shipping_address):
    """Insert a new customer and return the new customer_id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Customer (contact_number, shipping_address) VALUES (%s, %s)",
                (contact_number, shipping_address),
            )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
