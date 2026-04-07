# ReMarket — Second-hand Trading Platform

**COMP7640 Group 6 | Database Project**

A multi-vendor, multi-customer e-commerce platform for second-hand goods, built with Python and MySQL. Supports vendor management, product management, fuzzy tag search, order placement, and order modification.

---

## 1. Environment Requirements

| Requirement | Version  |
|-------------|----------|
| Python      | 3.8+     |
| MySQL       | 8.0+     |
| PyMySQL     | latest   |

Install the required Python package:

```bash
pip install pymysql
```

---

## 2. Database Configuration

Open the file `code/Backend/db.py` in any text editor (Notepad, VS Code, etc.) and change **only the password field** on line 9 to your own MySQL root password:

```python
"password": "your_password_here",   # <-- change this line only
```

Everything else (host, port, user, database name) can stay as-is if you are running MySQL locally with the default settings.

---

## 3. Database Setup

Run `code/group6_insert_sql.txt` to create the database, all tables, constraints, and sample data.

**Option A — MySQL command line:**
```bash
mysql -u root -p < code/group6_insert_sql.txt
```

**Option B — MySQL Workbench / DBeaver:**
Open `code/group6_insert_sql.txt` and execute the entire file.

This creates the `remarket` database with 6 tables and the following sample data:

| Table       | Sample Rows |
|-------------|-------------|
| Vendor      | 5           |
| Product     | 15          |
| Customer    | 3           |
| Order       | 5           |
| OrderItem   | 9           |
| Transaction | 6           |

To reset the database to its original state, re-run the same SQL file (it drops and recreates all tables automatically).

---

## 4. How to Run

### Option A — Graphical Interface (GUI)

```bash
cd code/Frontend
python gui.py
```

A window will open with 5 tabs covering all functional points.

### Option B — Command-line Interface (CLI)

```bash
cd code/Frontend
python main.py
```

The following menu will appear:

```
========================================
       Welcome to ReMarket
  Second-hand Trading Platform
========================================

--- Main Menu ---
  1. Vendor Management
  2. Product Management
  3. Search Products (by tag/name)
  4. Purchase
  5. Order Modification
  0. Exit
```

---

## 5. Implemented Features

### ① Vendor Management
| Action | GUI | CLI |
|--------|-----|-----|
| List all vendors | Vendors tab → Refresh | Menu 1 → 1 |
| Add new vendor | Vendors tab → Add Vendor | Menu 1 → 2 |

### ② Product Management
| Action | GUI | CLI |
|--------|-----|-----|
| Browse products by vendor | Products tab → select vendor → Browse | Menu 2 → 1 |
| Add new product for a vendor | Products tab → fill form → Add Product | Menu 2 → 2 |

### ③ Product Search (fuzzy LIKE matching)
| Action | GUI | CLI |
|--------|-----|-----|
| Search by keyword (matches product name OR tags) | Search tab → enter keyword → Search | Menu 3 |

> Note: search uses SQL `LIKE %keyword%` — not exact matching.

### ④ Purchase (Place Order)
| Action | GUI | CLI |
|--------|-----|-----|
| Select customer, add items to cart, confirm order | Purchase tab | Menu 4 |

- Stock is validated before order is confirmed
- If items span multiple vendors, one Transaction record is created per vendor

### ⑤ Order Modification
| Action | GUI | CLI |
|--------|-----|-----|
| Delete a specific product from a pending order | Order Modify tab → Load Order → Delete Selected Item | Menu 5 → 1 |
| Cancel entire order (pending orders only) | Order Modify tab → Load Order → Cancel Entire Order | Menu 5 → 2 |

- Cancelling an order restores stock and removes all related Transaction records
- Shipped orders cannot be cancelled

---

## 6. Project Structure

```
COMP7640 Group_Project/
├── README.md
├── code/
│   ├── group6_insert_sql.txt      # CREATE TABLE + sample data SQL
│   ├── Backend/
│   │   ├── db.py                  # MySQL connection (edit password here)
│   │   ├── vendor.py              # Vendor DAO — list, add
│   │   ├── product.py             # Product DAO — browse, add, search
│   │   ├── customer.py            # Customer DAO — list, add
│   │   ├── order.py               # Order DAO — place, delete item, cancel
│   │   └── transaction.py         # Transaction DAO — create, delete
│   └── Frontend/
│       ├── gui.py                 # GUI entry point (tkinter)
│       └── main.py                # CLI entry point
└── E-R Diagram.pdf
```

---

## 7. Demo Checklist

The following must be demonstrated during the project demo:

- [ ] **Search** — enter a keyword, verify fuzzy results appear
- [ ] **Place Order** — select customer, add products to cart, confirm
- [ ] **Modify Order** — delete an item from a pending order, or cancel the entire order
