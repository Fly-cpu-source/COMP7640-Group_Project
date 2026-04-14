# ReMarket — Second-hand Trading Platform

**COMP7640 Group 6 | Database Project**

A multi-vendor and multi-customer e-commerce platform for second-hand goods, built with Python and MySQL. Supports vendor management, product management, fuzzy tag search, order placement, and order modification.

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

Open the file `code/Backend/db.py` in any text editor (Notepad, VS Code, etc.) and change **only the password field** to your own MySQL root password:

```python
"password": "your_password_here",   # <-- change this line only
```

Everything else (host, port, user, database name) can stay as-is if you are running MySQL locally with the default settings.

---

## 3. Database Setup

Run `code/group6_insert_sql.txt` to create the database, all tables, constraints, and sample data.
```diff
- Please make sure to change it to the file path on your own computer.
```

**Option A — Command Prompt (cmd.exe, NOT PowerShell):**

Press Win+R, type CMD to enter, locate the path of **\bin\mysql.exe** and the path of **\code\group6_insert_sql.txt** on your computer, and add them to the code line as prompted.

```cmd
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < C:\Users\26764\Desktop\group6_project\code\group6_insert_sql.txt
```

**Option B — PowerShell (run from project root directory):**

Press Win+R, type PowerShell to enter, locate the path of **\code\group6_insert_sql.txt** and the path of **\bin\mysql.exe** on your computer, and add them to the prompted code line.

```powershell
Get-Content "C:\Users\26764\Desktop\group6_project\code\group6_insert_sql.txt" | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

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

### Graphical Interface (GUI)
After writing the code, press enter, input the password, then locate the \code\Frontend path on your computer and enter it using cd.
```bash
cd C:\Users\26764\Desktop\group6_project\code\Frontend
python gui.py
```

A window will open with 5 tabs covering all functional points.

---

## 5. Implemented Features

### ① Vendor Management
| Action | GUI |
|--------|-----|
| List all vendors | Vendors tab → Refresh |
| Add new vendor | Vendors tab → Add Vendor |

### ② Product Management
| Action | GUI |
|--------|-----|
| Browse products by vendor | Products tab → select vendor → Browse |
| Add new product for a vendor | Products tab → fill form → Add Product |

### ③ Product Search (fuzzy LIKE matching)
| Action | GUI |
|--------|-----|
| Search by keyword (matches product name OR tags) | Search tab → enter keyword → Search |

> Note: search uses SQL `LIKE %keyword%` — not exact matching.
> 
> Keywords list: electronics, phone, apple, mobile, laptop, computer, audio, headphones, book, textbook, science, algorithms, programming, software, fiction, classic, novel, fashion, jacket, vintage, clothing, bag, leather, accessories, shoes, sneakers, sportswear, furniture, shelf, home, storage, vacuum, cleaning, appliance, kitchen, coffee, sports, bike, cycling, yoga, fitness, exercise, tennis, racket, outdoor

### ④ Purchase (Place Order)
| Action | GUI |
|--------|-----|
| Select customer, add items to cart, confirm order | Purchase tab |

Stock is validated before order is confirmed. If items span multiple vendors, one Transaction record is created per vendor

### ⑤ Order Modification
| Action | GUI |
|--------|-----|
| Delete a specific product from a pending order | Order Modify tab → Load Order → Delete Selected Item |
| Cancel entire order (pending orders only) | Order Modify tab → Load Order → Cancel Entire Order |

Cancelling an order restores stock and removes all related Transaction records. Shipped orders cannot be cancelled

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
│       └── gui.py                 # GUI 






