# ReMarket — Second-hand Trading Platform

COMP7640 Group 6 Database Project

---

## 1. Environment Requirements

| Requirement | Version |
|-------------|---------|
| Python      | 3.8+    |
| MySQL       | 8.0+    |
| PyMySQL     | latest  |

Install PyMySQL:
```bash
pip install pymysql
```

---

## 2. Database Configuration

Open `code/Backend/db.py` and edit the `DB_CONFIG` dictionary:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "your_password_here",   # <-- change this
    "database": "remarket",
    ...
}
```

---

## 3. Database Setup

Run the SQL script to create the database, tables, and sample data:

**Option A — MySQL command line:**
```bash
mysql -u root -p < code/group6_insert_sql.txt
```

**Option B — MySQL Workbench / DBeaver:**
Open `code/group6_insert_sql.txt` and execute the entire file.

This will create the `remarket` database with 6 tables:
- `Vendor`, `Product`, `Customer`, `Order`, `OrderItem`, `Transaction`

And insert sample data:
- 5 vendors, 15 products, 3 customers, 5 orders, transaction records

---

## 4. How to Run

```bash
cd code/Frontend
python main.py
```

The CLI menu will appear:

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

## 5. Feature Overview

| Feature | Menu Option | Description |
|---------|-------------|-------------|
| List vendors | 1 → 1 | Show all vendors |
| Add vendor | 1 → 2 | Register a new vendor |
| Browse products | 2 → 1 | View products by vendor |
| Add product | 2 → 2 | Add product to a vendor |
| Search by tag | 3 | Fuzzy search by keyword |
| Place order | 4 | Select customer, add items, confirm |
| Delete item | 5 → 1 | Remove one product from a pending order |
| Cancel order | 5 → 2 | Cancel a pending order and restore stock |

---

## 6. Project Structure

```
COMP7640 Group_Project/
├── code/
│   ├── Backend/
│   │   ├── db.py           # Database connection
│   │   ├── vendor.py       # Vendor DAO
│   │   ├── product.py      # Product DAO
│   │   ├── customer.py     # Customer DAO
│   │   ├── order.py        # Order DAO
│   │   └── transaction.py  # Transaction DAO
│   ├── Frontend/
│   │   └── main.py         # CLI entry point
│   └── group6_insert_sql.txt
└── README.md
```
