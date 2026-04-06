"""
order.py — Order DAO for ReMarket.
Functional Point ④: Place order (generate order + transactions).
Functional Point ⑤: Delete item from order / Cancel entire order.
"""
from db import get_connection
from transaction import create_transactions_for_order, delete_transactions_for_order


def place_order(customer_id, items):
    """
    Place a new order atomically.

    Parameters
    ----------
    customer_id : int
    items : list of (product_id, quantity)

    Returns
    -------
    dict with keys 'order_id' and 'total_price', or raises RuntimeError on failure.

    Logic
    -----
    1. Validate stock for every item.
    2. INSERT Order row.
    3. For each item: INSERT OrderItem, UPDATE Product.stock_quantity.
    4. Group items by vendor_id → INSERT one Transaction per vendor.
    5. Everything is wrapped in a single DB transaction (COMMIT or ROLLBACK).
    """
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cur:
            # Step 1: validate stock and fetch unit prices + vendor_id
            order_items = []
            for product_id, qty in items:
                cur.execute(
                    "SELECT product_id, product_name, price, stock_quantity, vendor_id "
                    "FROM Product WHERE product_id = %s FOR UPDATE",
                    (product_id,),
                )
                product = cur.fetchone()
                if product is None:
                    raise RuntimeError(f"Product {product_id} does not exist.")
                if product["stock_quantity"] < qty:
                    raise RuntimeError(
                        f"Insufficient stock for '{product['product_name']}' "
                        f"(available: {product['stock_quantity']}, requested: {qty})."
                    )
                order_items.append({
                    "product_id":  product_id,
                    "quantity":    qty,
                    "unit_price":  product["price"],
                    "vendor_id":   product["vendor_id"],
                    "subtotal":    product["price"] * qty,
                })

            total_price = sum(i["subtotal"] for i in order_items)

            # Step 2: INSERT Order
            cur.execute(
                "INSERT INTO `Order` (total_price, status, customer_id) VALUES (%s, 'pending', %s)",
                (total_price, customer_id),
            )
            order_id = cur.lastrowid

            # Step 3: INSERT OrderItems and decrement stock
            for item in order_items:
                cur.execute(
                    "INSERT INTO OrderItem (order_id, product_id, quantity, unit_price) "
                    "VALUES (%s, %s, %s, %s)",
                    (order_id, item["product_id"], item["quantity"], item["unit_price"]),
                )
                cur.execute(
                    "UPDATE Product SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                    (item["quantity"], item["product_id"]),
                )

        # Step 4: build vendor → subtotal map and insert Transactions
        vendor_amounts = {}
        for item in order_items:
            vendor_amounts[item["vendor_id"]] = (
                vendor_amounts.get(item["vendor_id"], 0) + item["subtotal"]
            )
        create_transactions_for_order(conn, order_id, vendor_amounts)

        conn.commit()
        return {"order_id": order_id, "total_price": total_price}

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_order_by_id(order_id):
    """Return an order dict with its items, or None if not found."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM `Order` WHERE order_id = %s", (order_id,))
            order = cur.fetchone()
            if order is None:
                return None
            cur.execute(
                """
                SELECT oi.*, p.product_name, v.vendor_id, v.business_name AS vendor_name
                FROM OrderItem oi
                JOIN Product p ON oi.product_id = p.product_id
                JOIN Vendor  v ON p.vendor_id = v.vendor_id
                WHERE oi.order_id = %s
                """,
                (order_id,),
            )
            order["items"] = cur.fetchall()
            return order
    finally:
        conn.close()


def list_orders_by_customer(customer_id):
    """Return all orders placed by a customer (without items)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM `Order` WHERE customer_id = %s ORDER BY order_id",
                (customer_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()


def delete_item_from_order(order_id, product_id):
    """
    Remove one product from a pending order.
    Recalculates total_price. Returns True on success, raises RuntimeError otherwise.
    """
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cur:
            # Check order exists and is pending
            cur.execute(
                "SELECT status FROM `Order` WHERE order_id = %s FOR UPDATE",
                (order_id,),
            )
            order = cur.fetchone()
            if order is None:
                raise RuntimeError(f"Order {order_id} does not exist.")
            if order["status"] != "pending":
                raise RuntimeError(
                    f"Cannot modify order {order_id}: status is '{order['status']}' (must be 'pending')."
                )

            # Check item exists in order
            cur.execute(
                "SELECT quantity, unit_price FROM OrderItem WHERE order_id = %s AND product_id = %s",
                (order_id, product_id),
            )
            item = cur.fetchone()
            if item is None:
                raise RuntimeError(f"Product {product_id} is not in order {order_id}.")

            item_total = item["quantity"] * item["unit_price"]

            # Restore stock
            cur.execute(
                "UPDATE Product SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                (item["quantity"], product_id),
            )

            # Remove item
            cur.execute(
                "DELETE FROM OrderItem WHERE order_id = %s AND product_id = %s",
                (order_id, product_id),
            )

            # Check remaining items — if none left, cancel the order
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM OrderItem WHERE order_id = %s",
                (order_id,),
            )
            remaining = cur.fetchone()["cnt"]

            if remaining == 0:
                # No items left: cancel the order and delete transactions
                delete_transactions_for_order(conn, order_id)
                cur.execute(
                    "UPDATE `Order` SET total_price = 0, status = 'cancelled' WHERE order_id = %s",
                    (order_id,),
                )
            else:
                # Recalculate total_price
                cur.execute(
                    "UPDATE `Order` SET total_price = total_price - %s WHERE order_id = %s",
                    (item_total, order_id),
                )
                # Update the affected vendor's transaction amount
                cur.execute(
                    "SELECT vendor_id FROM Product WHERE product_id = %s", (product_id,)
                )
                vendor_id = cur.fetchone()["vendor_id"]
                cur.execute(
                    "UPDATE Transaction SET amount = amount - %s "
                    "WHERE order_id = %s AND vendor_id = %s",
                    (item_total, order_id, vendor_id),
                )
                # Remove transaction row if its amount drops to 0
                cur.execute(
                    "DELETE FROM Transaction WHERE order_id = %s AND vendor_id = %s AND amount <= 0",
                    (order_id, vendor_id),
                )

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cancel_order(order_id):
    """
    Cancel an order that is still pending.
    Steps:
      1. Delete all Transaction rows for this order.
      2. Restore stock for every OrderItem.
      3. Set Order.status = 'cancelled'.
    Raises RuntimeError if order is already shipped or cancelled.
    """
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cur:
            # Check order status
            cur.execute(
                "SELECT status FROM `Order` WHERE order_id = %s FOR UPDATE",
                (order_id,),
            )
            order = cur.fetchone()
            if order is None:
                raise RuntimeError(f"Order {order_id} does not exist.")
            if order["status"] == "shipped":
                raise RuntimeError(
                    f"Cannot cancel order {order_id}: order has already been shipped."
                )
            if order["status"] == "cancelled":
                raise RuntimeError(f"Order {order_id} is already cancelled.")

            # Step 1: delete all transactions for this order
            delete_transactions_for_order(conn, order_id)

            # Step 2: restore stock for each order item
            cur.execute(
                "SELECT product_id, quantity FROM OrderItem WHERE order_id = %s",
                (order_id,),
            )
            items = cur.fetchall()
            for item in items:
                cur.execute(
                    "UPDATE Product SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                    (item["quantity"], item["product_id"]),
                )

            # Step 3: mark order as cancelled
            cur.execute(
                "UPDATE `Order` SET status = 'cancelled' WHERE order_id = %s",
                (order_id,),
            )

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
