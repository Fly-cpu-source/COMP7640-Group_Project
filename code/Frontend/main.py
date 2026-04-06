"""
main.py — CLI entry point for ReMarket.
Run: python main.py
"""
import sys
import os

# Add Backend directory to path so we can import DAOs directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Backend"))

import vendor as vendor_dao
import product as product_dao
import customer as customer_dao
import order as order_dao


# ── Helpers ──────────────────────────────────────────────────────────────────

def input_int(prompt, min_val=None, max_val=None):
    """Prompt user for an integer, re-asking on invalid input."""
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val is not None and val < min_val:
                print(f"  Please enter a value >= {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"  Please enter a value <= {max_val}.")
                continue
            return val
        except ValueError:
            print("  Invalid input. Please enter an integer.")


def input_float(prompt, min_val=0.0):
    """Prompt user for a non-negative float."""
    while True:
        try:
            val = float(input(prompt).strip())
            if val < min_val:
                print(f"  Please enter a value >= {min_val}.")
                continue
            return val
        except ValueError:
            print("  Invalid input. Please enter a number.")


def print_table(rows, columns):
    """Print a list of dicts as a simple text table."""
    if not rows:
        print("  (no records found)")
        return
    col_widths = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            col_widths[c] = max(col_widths[c], len(str(row.get(c, ""))))
    header = "  " + "  ".join(c.ljust(col_widths[c]) for c in columns)
    separator = "  " + "  ".join("-" * col_widths[c] for c in columns)
    print(header)
    print(separator)
    for row in rows:
        print("  " + "  ".join(str(row.get(c, "")).ljust(col_widths[c]) for c in columns))


# ── Menus ────────────────────────────────────────────────────────────────────

def menu_vendor():
    """Vendor Management sub-menu."""
    while True:
        print("\n--- Vendor Management ---")
        print("  1. List all vendors")
        print("  2. Add new vendor")
        print("  0. Back")
        choice = input("Select: ").strip()

        if choice == "1":
            vendors = vendor_dao.list_vendors()
            print()
            print_table(vendors, ["vendor_id", "business_name", "average_rating", "geographical_presence"])

        elif choice == "2":
            name = input("  Business name: ").strip()
            if not name:
                print("  Name cannot be empty.")
                continue
            location = input("  Location: ").strip()
            new_id = vendor_dao.add_vendor(name, location)
            print(f"  Vendor added successfully (vendor_id = {new_id}).")

        elif choice == "0":
            break
        else:
            print("  Invalid option.")


def menu_product():
    """Product Management sub-menu."""
    while True:
        print("\n--- Product Management ---")
        print("  1. Browse products by vendor")
        print("  2. Add new product")
        print("  0. Back")
        choice = input("Select: ").strip()

        if choice == "1":
            vendors = vendor_dao.list_vendors()
            print()
            print_table(vendors, ["vendor_id", "business_name"])
            vendor_id = input_int("  Enter vendor_id: ", min_val=1)
            v = vendor_dao.get_vendor_by_id(vendor_id)
            if v is None:
                print(f"  Vendor {vendor_id} not found.")
                continue
            products = product_dao.get_products_by_vendor(vendor_id)
            print(f"\n  Products from '{v['business_name']}':")
            print_table(products, ["product_id", "product_name", "price", "stock_quantity", "tags"])

        elif choice == "2":
            vendors = vendor_dao.list_vendors()
            print()
            print_table(vendors, ["vendor_id", "business_name"])
            vendor_id = input_int("  Enter vendor_id: ", min_val=1)
            v = vendor_dao.get_vendor_by_id(vendor_id)
            if v is None:
                print(f"  Vendor {vendor_id} not found.")
                continue
            name  = input("  Product name: ").strip()
            if not name:
                print("  Name cannot be empty.")
                continue
            price = input_float("  Price (HKD): ", min_val=0.01)
            stock = input_int("  Stock quantity: ", min_val=0)
            tags  = input("  Tags (comma-separated, e.g. electronics,phone): ").strip()
            new_id = product_dao.add_product(vendor_id, name, price, stock, tags)
            print(f"  Product added successfully (product_id = {new_id}).")

        elif choice == "0":
            break
        else:
            print("  Invalid option.")


def menu_search():
    """Search products by tag or name (fuzzy LIKE)."""
    keyword = input("\nEnter search keyword: ").strip()
    if not keyword:
        print("  Keyword cannot be empty.")
        return
    results = product_dao.search_by_tag(keyword)
    print(f"\n  Results for '{keyword}':")
    print_table(results, ["product_id", "product_name", "price", "stock_quantity", "tags", "vendor_name"])


def menu_purchase():
    """Purchase sub-menu: select customer, add items, confirm order."""
    print("\n--- Purchase ---")

    # Select or create customer
    customers = customer_dao.list_customers()
    print()
    print_table(customers, ["customer_id", "contact_number", "shipping_address"])
    print("  (enter 0 to create a new customer)")
    customer_id = input_int("  Enter customer_id: ", min_val=0)

    if customer_id == 0:
        contact = input("  Contact number: ").strip()
        address = input("  Shipping address: ").strip()
        customer_id = customer_dao.add_customer(contact, address)
        print(f"  New customer created (customer_id = {customer_id}).")
    else:
        c = customer_dao.get_customer_by_id(customer_id)
        if c is None:
            print(f"  Customer {customer_id} not found.")
            return

    # Build cart
    cart = []  # list of (product_id, quantity)
    print("\n  Add items to cart. Enter product_id = 0 to finish.")
    while True:
        product_id = input_int("  product_id (0 to finish): ", min_val=0)
        if product_id == 0:
            break
        p = product_dao.get_product_by_id(product_id)
        if p is None:
            print(f"  Product {product_id} not found.")
            continue
        if p["stock_quantity"] == 0:
            print(f"  '{p['product_name']}' is out of stock.")
            continue
        qty = input_int(f"  Quantity (max {p['stock_quantity']}): ", min_val=1, max_val=p["stock_quantity"])
        cart.append((product_id, qty))
        print(f"  Added: {p['product_name']} x{qty} @ HKD {p['price']:.2f}")

    if not cart:
        print("  Cart is empty. Order cancelled.")
        return

    # Confirm
    print("\n  Order summary:")
    total = 0
    for product_id, qty in cart:
        p = product_dao.get_product_by_id(product_id)
        subtotal = p["price"] * qty
        total += subtotal
        print(f"    {p['product_name']} x{qty} = HKD {subtotal:.2f}")
    print(f"  Total: HKD {total:.2f}")
    confirm = input("  Confirm order? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Order not placed.")
        return

    try:
        result = order_dao.place_order(customer_id, cart)
        print(f"  Order placed successfully! order_id = {result['order_id']}, total = HKD {result['total_price']:.2f}")
    except RuntimeError as e:
        print(f"  Error: {e}")


def menu_order_modification():
    """Order Modification sub-menu."""
    while True:
        print("\n--- Order Modification ---")
        print("  1. Delete item from order")
        print("  2. Cancel entire order")
        print("  0. Back")
        choice = input("Select: ").strip()

        if choice == "1":
            order_id   = input_int("  Enter order_id: ", min_val=1)
            order = order_dao.get_order_by_id(order_id)
            if order is None:
                print(f"  Order {order_id} not found.")
                continue
            print(f"\n  Order {order_id} (status: {order['status']}):")
            print_table(order["items"], ["product_id", "product_name", "quantity", "unit_price"])
            product_id = input_int("  Enter product_id to remove: ", min_val=1)
            try:
                order_dao.delete_item_from_order(order_id, product_id)
                print(f"  Item {product_id} removed from order {order_id}.")
            except RuntimeError as e:
                print(f"  Error: {e}")

        elif choice == "2":
            order_id = input_int("  Enter order_id to cancel: ", min_val=1)
            order = order_dao.get_order_by_id(order_id)
            if order is None:
                print(f"  Order {order_id} not found.")
                continue
            print(f"\n  Order {order_id} — status: {order['status']}, total: HKD {order['total_price']:.2f}")
            confirm = input("  Confirm cancellation? (y/n): ").strip().lower()
            if confirm != "y":
                print("  Cancellation aborted.")
                continue
            try:
                order_dao.cancel_order(order_id)
                print(f"  Order {order_id} has been cancelled and stock restored.")
            except RuntimeError as e:
                print(f"  Error: {e}")

        elif choice == "0":
            break
        else:
            print("  Invalid option.")


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 40)
    print("       Welcome to ReMarket")
    print("  Second-hand Trading Platform")
    print("=" * 40)

    while True:
        print("\n--- Main Menu ---")
        print("  1. Vendor Management")
        print("  2. Product Management")
        print("  3. Search Products (by tag/name)")
        print("  4. Purchase")
        print("  5. Order Modification")
        print("  0. Exit")
        choice = input("Select: ").strip()

        if choice == "1":
            menu_vendor()
        elif choice == "2":
            menu_product()
        elif choice == "3":
            menu_search()
        elif choice == "4":
            menu_purchase()
        elif choice == "5":
            menu_order_modification()
        elif choice == "0":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("  Invalid option. Please try again.")


if __name__ == "__main__":
    main()
