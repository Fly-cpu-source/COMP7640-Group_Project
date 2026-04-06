"""
transaction.py — Transaction DAO for ReMarket.
One Transaction row is created per vendor involved in an order.
Transactions are deleted when an order is cancelled.
"""
from db import get_connection


def create_transactions_for_order(conn, order_id, vendor_amounts):
    """
    Insert one Transaction row per vendor within an existing DB connection/transaction.
    vendor_amounts: dict {vendor_id: subtotal_amount}
    Uses the caller's connection so this participates in the same atomic transaction.
    """
    with conn.cursor() as cur:
        for vendor_id, amount in vendor_amounts.items():
            cur.execute(
                """
                INSERT INTO Transaction (amount, order_id, vendor_id)
                VALUES (%s, %s, %s)
                """,
                (amount, order_id, vendor_id),
            )


def delete_transactions_for_order(conn, order_id):
    """
    Delete all Transaction rows for a given order.
    Called during order cancellation within an existing DB connection/transaction.
    """
    with conn.cursor() as cur:
        cur.execute("DELETE FROM Transaction WHERE order_id = %s", (order_id,))


def get_transactions_by_order(order_id):
    """Return all transaction records for a given order."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT t.*, v.business_name AS vendor_name
                FROM Transaction t
                JOIN Vendor v ON t.vendor_id = v.vendor_id
                WHERE t.order_id = %s
                """,
                (order_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()
