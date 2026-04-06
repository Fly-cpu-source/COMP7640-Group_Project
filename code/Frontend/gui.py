"""
gui.py — Tkinter GUI entry point for ReMarket.
Run: python gui.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Backend"))

import tkinter as tk
from tkinter import ttk, messagebox

import vendor as vendor_dao
import product as product_dao
import customer as customer_dao
import order as order_dao
import transaction as transaction_dao

# ── Colour / Style constants ──────────────────────────────────────────────────
BG        = "#F5F5F0"
ACCENT    = "#2C6E49"
ACCENT2   = "#52B788"
DANGER    = "#C1121F"
TEXT      = "#1B1B1B"
SUBTLE    = "#6B705C"
WHITE     = "#FFFFFF"
ENTRY_BG  = "#FFFFFF"
ROW_ODD   = "#F0F4F0"
ROW_EVEN  = "#FFFFFF"
FONT_BODY = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI Semibold", 10)
FONT_TITL = ("Segoe UI Semibold", 13)


# ── Utility widgets ───────────────────────────────────────────────────────────

def make_table(parent, columns, height=12):
    """Return a configured (frame, treeview) pair with scrollbar."""
    frame = tk.Frame(parent, bg=BG)
    scrollbar = ttk.Scrollbar(frame, orient="vertical")
    tv = ttk.Treeview(
        frame, columns=columns, show="headings",
        height=height, yscrollcommand=scrollbar.set,
        selectmode="browse",
    )
    scrollbar.config(command=tv.yview)
    for col in columns:
        tv.heading(col, text=col.replace("_", " ").title())
        tv.column(col, anchor="w", minwidth=60, width=120)
    tv.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    tv.tag_configure("odd",  background=ROW_ODD)
    tv.tag_configure("even", background=ROW_EVEN)
    return frame, tv


def fill_table(tv, rows, columns):
    """Clear and repopulate a Treeview."""
    tv.delete(*tv.get_children())
    for i, row in enumerate(rows):
        tag = "odd" if i % 2 else "even"
        tv.insert("", "end", values=[row.get(c, "") for c in columns], tags=(tag,))


def label_entry(parent, text, row, col=0, width=22):
    """Return (Label, Entry) placed on a grid."""
    tk.Label(parent, text=text, bg=BG, fg=TEXT, font=FONT_BODY,
             anchor="w").grid(row=row, column=col, sticky="w", padx=6, pady=4)
    e = ttk.Entry(parent, width=width)
    e.grid(row=row, column=col + 1, sticky="ew", padx=6, pady=4)
    return e


def btn(parent, text, cmd, danger=False, **kw):
    """Styled button."""
    bg = DANGER if danger else ACCENT
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=WHITE, activebackground=ACCENT2,
                  font=FONT_BODY, relief="flat", padx=14, pady=5,
                  cursor="hand2", **kw)
    return b


def section_title(parent, text):
    tk.Label(parent, text=text, bg=BG, fg=ACCENT, font=FONT_TITL).pack(
        anchor="w", padx=14, pady=(12, 4))


# ── Tab 1: Vendor Management ──────────────────────────────────────────────────

class VendorTab(tk.Frame):
    COLS = ["vendor_id", "business_name", "average_rating", "geographical_presence"]

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()
        self.refresh()

    def _build(self):
        section_title(self, "All Vendors")
        tf, self.tv = make_table(self, self.COLS, height=10)
        tf.pack(fill="both", expand=True, padx=14, pady=4)
        btn(self, "Refresh", self.refresh).pack(anchor="e", padx=14, pady=2)

        ttk.Separator(self).pack(fill="x", padx=14, pady=8)
        section_title(self, "Add New Vendor")

        form = tk.Frame(self, bg=BG)
        form.pack(fill="x", padx=14)
        self.e_name = label_entry(form, "Business Name:", 0)
        self.e_loc  = label_entry(form, "Location:",      1)
        form.columnconfigure(1, weight=1)
        btn(form, "Add Vendor", self._add).grid(
            row=2, column=0, columnspan=2, pady=8, sticky="w", padx=6)

    def refresh(self):
        fill_table(self.tv, vendor_dao.list_vendors(), self.COLS)

    def _add(self):
        name = self.e_name.get().strip()
        loc  = self.e_loc.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Business name is required.")
            return
        vid = vendor_dao.add_vendor(name, loc)
        messagebox.showinfo("Success", f"Vendor added (ID = {vid})")
        self.e_name.delete(0, "end")
        self.e_loc.delete(0, "end")
        self.refresh()


# ── Tab 2: Product Management ─────────────────────────────────────────────────

class ProductTab(tk.Frame):
    COLS = ["product_id", "product_name", "price", "stock_quantity", "tags", "vendor_id"]

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()
        self._load_vendors()

    def _build(self):
        section_title(self, "Browse Products by Vendor")

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=4)
        tk.Label(top, text="Select Vendor:", bg=BG, font=FONT_BODY).pack(side="left")
        self.vendor_var = tk.StringVar()
        self.vendor_cb  = ttk.Combobox(top, textvariable=self.vendor_var,
                                        state="readonly", width=30)
        self.vendor_cb.pack(side="left", padx=8)
        btn(top, "Browse", self._browse).pack(side="left")

        tf, self.tv = make_table(self, self.COLS, height=9)
        tf.pack(fill="both", expand=True, padx=14, pady=4)

        ttk.Separator(self).pack(fill="x", padx=14, pady=8)
        section_title(self, "Add New Product")

        form = tk.Frame(self, bg=BG)
        form.pack(fill="x", padx=14)
        tk.Label(form, text="Vendor:", bg=BG, font=FONT_BODY,
                 anchor="w").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.add_vendor_var = tk.StringVar()
        self.add_vendor_cb  = ttk.Combobox(form, textvariable=self.add_vendor_var,
                                            state="readonly", width=28)
        self.add_vendor_cb.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        self.e_pname = label_entry(form, "Product Name:", 1)
        self.e_price = label_entry(form, "Price (HKD):",  2)
        self.e_stock = label_entry(form, "Stock:",        3)
        self.e_tags  = label_entry(form, "Tags (comma):", 4)
        form.columnconfigure(1, weight=1)
        btn(form, "Add Product", self._add).grid(
            row=5, column=0, columnspan=2, pady=8, sticky="w", padx=6)

    def _load_vendors(self):
        vendors = vendor_dao.list_vendors()
        opts = [f"{v['vendor_id']} - {v['business_name']}" for v in vendors]
        self.vendor_cb["values"]     = opts
        self.add_vendor_cb["values"] = opts
        if opts:
            self.vendor_cb.current(0)
            self.add_vendor_cb.current(0)

    def _browse(self):
        sel = self.vendor_var.get()
        if not sel:
            return
        vid = int(sel.split(" - ")[0])
        fill_table(self.tv, product_dao.get_products_by_vendor(vid), self.COLS)

    def _add(self):
        sel = self.add_vendor_var.get()
        if not sel:
            messagebox.showwarning("Input Error", "Select a vendor.")
            return
        vid  = int(sel.split(" - ")[0])
        name = self.e_pname.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Product name is required.")
            return
        try:
            price = float(self.e_price.get())
            stock = int(self.e_stock.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Price must be a number, Stock must be an integer.")
            return
        tags = self.e_tags.get().strip()
        pid  = product_dao.add_product(vid, name, price, stock, tags)
        messagebox.showinfo("Success", f"Product added (ID = {pid})")
        for e in [self.e_pname, self.e_price, self.e_stock, self.e_tags]:
            e.delete(0, "end")
        self._load_vendors()


# ── Tab 3: Search ─────────────────────────────────────────────────────────────

class SearchTab(tk.Frame):
    COLS = ["product_id", "product_name", "price", "stock_quantity", "tags", "vendor_name"]

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        section_title(self, "Search Products (fuzzy match on name & tags)")

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=8)
        tk.Label(top, text="Keyword:", bg=BG, font=FONT_BODY).pack(side="left")
        self.e_kw = ttk.Entry(top, width=32)
        self.e_kw.pack(side="left", padx=8)
        self.e_kw.bind("<Return>", lambda _: self._search())
        btn(top, "Search", self._search).pack(side="left")

        self.lbl_count = tk.Label(self, text="", bg=BG, fg=SUBTLE, font=FONT_BODY)
        self.lbl_count.pack(anchor="w", padx=14)

        tf, self.tv = make_table(self, self.COLS, height=16)
        tf.pack(fill="both", expand=True, padx=14, pady=4)

    def _search(self):
        kw = self.e_kw.get().strip()
        if not kw:
            messagebox.showwarning("Input Error", "Please enter a keyword.")
            return
        results = product_dao.search_by_tag(kw)
        fill_table(self.tv, results, self.COLS)
        self.lbl_count.config(text=f"{len(results)} result(s) for '{kw}'")


# ── Tab 4: Purchase ───────────────────────────────────────────────────────────

class PurchaseTab(tk.Frame):
    CART_COLS = ["product_id", "product_name", "price", "qty", "subtotal"]

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.cart = []   # list of dicts
        self._build()
        self._load_customers()

    def _build(self):
        section_title(self, "Place Order")

        # ── Customer row ──
        cust_row = tk.Frame(self, bg=BG)
        cust_row.pack(fill="x", padx=14, pady=4)
        tk.Label(cust_row, text="Customer:", bg=BG, font=FONT_BODY).pack(side="left")
        self.cust_var = tk.StringVar()
        self.cust_cb  = ttk.Combobox(cust_row, textvariable=self.cust_var,
                                      state="readonly", width=36)
        self.cust_cb.pack(side="left", padx=8)

        # ── Add item row ──
        item_row = tk.Frame(self, bg=BG)
        item_row.pack(fill="x", padx=14, pady=4)
        tk.Label(item_row, text="Product ID:", bg=BG, font=FONT_BODY).pack(side="left")
        self.e_pid = ttk.Entry(item_row, width=8)
        self.e_pid.pack(side="left", padx=6)
        tk.Label(item_row, text="Qty:", bg=BG, font=FONT_BODY).pack(side="left")
        self.e_qty = ttk.Entry(item_row, width=6)
        self.e_qty.pack(side="left", padx=6)
        self.e_qty.insert(0, "1")
        btn(item_row, "Add to Cart", self._add_to_cart).pack(side="left", padx=6)
        btn(item_row, "Remove Selected", self._remove_item, danger=True).pack(side="left", padx=2)

        # ── Cart table ──
        tf, self.cart_tv = make_table(self, self.CART_COLS, height=8)
        tf.pack(fill="both", expand=True, padx=14, pady=4)

        # ── Total + confirm ──
        bot = tk.Frame(self, bg=BG)
        bot.pack(fill="x", padx=14, pady=6)
        self.lbl_total = tk.Label(bot, text="Total: HKD 0.00",
                                   bg=BG, fg=ACCENT, font=("Segoe UI Semibold", 12))
        self.lbl_total.pack(side="left")
        btn(bot, "Clear Cart", self._clear_cart, danger=True).pack(side="right", padx=4)
        btn(bot, "Confirm Order", self._confirm).pack(side="right", padx=4)

    def _load_customers(self):
        customers = customer_dao.list_customers()
        opts = [f"{c['customer_id']} - {c['shipping_address']}" for c in customers]
        self.cust_cb["values"] = opts
        if opts:
            self.cust_cb.current(0)

    def _add_to_cart(self):
        try:
            pid = int(self.e_pid.get())
            qty = int(self.e_qty.get())
            if qty < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Enter a valid Product ID and Quantity >= 1.")
            return
        p = product_dao.get_product_by_id(pid)
        if p is None:
            messagebox.showwarning("Not Found", f"Product {pid} does not exist.")
            return
        if p["stock_quantity"] < qty:
            messagebox.showwarning("Stock Error",
                f"Only {p['stock_quantity']} in stock for '{p['product_name']}'.")
            return
        # Check if already in cart
        for item in self.cart:
            if item["product_id"] == pid:
                messagebox.showwarning("Duplicate", f"Product {pid} is already in cart.")
                return
        self.cart.append({
            "product_id":   pid,
            "product_name": p["product_name"],
            "price":        float(p["price"]),
            "qty":          qty,
            "subtotal":     float(p["price"]) * qty,
        })
        self._refresh_cart()
        self.e_pid.delete(0, "end")
        self.e_qty.delete(0, "end")
        self.e_qty.insert(0, "1")

    def _remove_item(self):
        sel = self.cart_tv.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a row to remove.")
            return
        idx = self.cart_tv.index(sel[0])
        self.cart.pop(idx)
        self._refresh_cart()

    def _clear_cart(self):
        self.cart.clear()
        self._refresh_cart()

    def _refresh_cart(self):
        fill_table(self.cart_tv, self.cart, self.CART_COLS)
        total = sum(i["subtotal"] for i in self.cart)
        self.lbl_total.config(text=f"Total: HKD {total:.2f}")

    def _confirm(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add at least one item.")
            return
        sel = self.cust_var.get()
        if not sel:
            messagebox.showwarning("No Customer", "Select a customer.")
            return
        cid   = int(sel.split(" - ")[0])
        items = [(i["product_id"], i["qty"]) for i in self.cart]
        try:
            result = order_dao.place_order(cid, items)
            messagebox.showinfo("Order Placed",
                f"Order #{result['order_id']} placed!\nTotal: HKD {result['total_price']:.2f}")
            self._clear_cart()
        except RuntimeError as e:
            messagebox.showerror("Order Failed", str(e))


# ── Tab 5: Order Modification ─────────────────────────────────────────────────

class OrderTab(tk.Frame):
    ORDER_COLS = ["order_id", "order_date", "total_price", "status", "customer_id"]
    ITEM_COLS  = ["product_id", "product_name", "quantity", "unit_price", "vendor_name"]

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        section_title(self, "Modify / Cancel Order")

        # ── Lookup row ──
        lookup = tk.Frame(self, bg=BG)
        lookup.pack(fill="x", padx=14, pady=6)
        tk.Label(lookup, text="Order ID:", bg=BG, font=FONT_BODY).pack(side="left")
        self.e_oid = ttk.Entry(lookup, width=10)
        self.e_oid.pack(side="left", padx=6)
        btn(lookup, "Load Order", self._load).pack(side="left")

        # ── Order info ──
        self.lbl_info = tk.Label(self, text="", bg=BG, fg=SUBTLE, font=FONT_BODY)
        self.lbl_info.pack(anchor="w", padx=14)

        # ── Items table ──
        tk.Label(self, text="Order Items:", bg=BG, fg=TEXT,
                 font=FONT_HEAD).pack(anchor="w", padx=14, pady=(8, 2))
        tf, self.item_tv = make_table(self, self.ITEM_COLS, height=8)
        tf.pack(fill="both", expand=True, padx=14, pady=4)

        # ── Action buttons ──
        acts = tk.Frame(self, bg=BG)
        acts.pack(fill="x", padx=14, pady=8)
        btn(acts, "Delete Selected Item", self._delete_item, danger=True).pack(side="left", padx=4)
        btn(acts, "Cancel Entire Order",  self._cancel_order, danger=True).pack(side="left", padx=4)

        # ── Transaction info ──
        ttk.Separator(self).pack(fill="x", padx=14, pady=4)
        tk.Label(self, text="Transactions for this Order:",
                 bg=BG, fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=14, pady=(4, 2))
        txn_cols = ["transaction_id", "vendor_name", "amount", "payment_date"]
        tf2, self.txn_tv = make_table(self, txn_cols, height=4)
        tf2.pack(fill="x", padx=14, pady=4)

        self._current_order = None

    def _load(self):
        try:
            oid = int(self.e_oid.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Enter a valid Order ID.")
            return
        order = order_dao.get_order_by_id(oid)
        if order is None:
            messagebox.showwarning("Not Found", f"Order {oid} not found.")
            return
        self._current_order = order
        self.lbl_info.config(
            text=f"Order #{order['order_id']}  |  Status: {order['status']}  "
                 f"|  Total: HKD {order['total_price']:.2f}  "
                 f"|  Customer: {order['customer_id']}")
        fill_table(self.item_tv, order["items"], self.ITEM_COLS)
        txns = transaction_dao.get_transactions_by_order(oid)
        fill_table(self.txn_tv, txns, ["transaction_id", "vendor_name", "amount", "payment_date"])

    def _delete_item(self):
        if not self._current_order:
            messagebox.showwarning("No Order", "Load an order first.")
            return
        sel = self.item_tv.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an item row to delete.")
            return
        vals   = self.item_tv.item(sel[0], "values")
        pid    = int(vals[0])
        pname  = vals[1]
        oid    = self._current_order["order_id"]
        if not messagebox.askyesno("Confirm", f"Remove '{pname}' from Order #{oid}?"):
            return
        try:
            order_dao.delete_item_from_order(oid, pid)
            messagebox.showinfo("Done", f"Item '{pname}' removed.")
            self._load()
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))

    def _cancel_order(self):
        if not self._current_order:
            messagebox.showwarning("No Order", "Load an order first.")
            return
        oid = self._current_order["order_id"]
        if not messagebox.askyesno("Confirm", f"Cancel Order #{oid}? This cannot be undone."):
            return
        try:
            order_dao.cancel_order(oid)
            messagebox.showinfo("Cancelled", f"Order #{oid} has been cancelled and stock restored.")
            self._load()
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))


# ── Main App ──────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ReMarket — Second-hand Trading Platform")
        self.geometry("860x680")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._apply_styles()
        self._build()

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",        background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",    background="#D8E8DC", foreground=TEXT,
                         font=FONT_HEAD, padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", WHITE)])
        style.configure("TEntry",           fieldbackground=ENTRY_BG, padding=4)
        style.configure("TCombobox",        fieldbackground=ENTRY_BG)
        style.configure("Treeview",         background=WHITE, foreground=TEXT,
                         rowheight=24, font=FONT_BODY)
        style.configure("Treeview.Heading", background=ACCENT, foreground=WHITE,
                         font=FONT_HEAD)
        style.map("Treeview", background=[("selected", ACCENT2)])
        style.configure("TSeparator",       background="#C8D8C8")

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=ACCENT, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="ReMarket", bg=ACCENT, fg=WHITE,
                 font=("Segoe UI Semibold", 18)).pack(side="left", padx=18, pady=10)
        tk.Label(hdr, text="Second-hand Trading Platform",
                 bg=ACCENT, fg="#A8D5B5",
                 font=("Segoe UI", 10)).pack(side="left", pady=10)

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        tabs = [
            ("Vendors",        VendorTab),
            ("Products",       ProductTab),
            ("Search",         SearchTab),
            ("Purchase",       PurchaseTab),
            ("Order Modify",   OrderTab),
        ]
        frames = []
        for name, cls in tabs:
            frame = cls(nb)
            nb.add(frame, text=f"  {name}  ")
            frames.append(frame)

        # Keep references for tab-switch refresh
        self._product_tab  = frames[1]   # ProductTab
        self._purchase_tab = frames[3]   # PurchaseTab

        # Refresh vendor / customer lists whenever the user switches tabs
        def on_tab_changed(event):
            idx = nb.index(nb.select())
            if idx == 1:   # Products tab
                self._product_tab._load_vendors()
            elif idx == 3: # Purchase tab
                self._purchase_tab._load_customers()

        nb.bind("<<NotebookTabChanged>>", on_tab_changed)


if __name__ == "__main__":
    app = App()
    app.mainloop()
