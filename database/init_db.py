import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def create_sample_database():
    """Create a sample business database with complex schema and data quality issues"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'business_data.db')
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables with intentionally bad schema names
    
    # Customer table (with poor naming)
    cursor.execute('''
    CREATE TABLE cust_tbl (
        id INTEGER PRIMARY KEY,
        nm VARCHAR(100),
        em VARCHAR(100),
        ph VARCHAR(20),
        addr TEXT,
        reg_dt DATE,
        seg VARCHAR(20),
        status VARCHAR(10)
    )
    ''')
    
    # Products table (with unnamed columns)
    cursor.execute('''
    CREATE TABLE prod_master (
        pid INTEGER PRIMARY KEY,
        pname TEXT,
        cat VARCHAR(50),
        subcategory VARCHAR(50),
        price DECIMAL(10,2),
        cost DECIMAL(10,2),
        col6 VARCHAR(50),  -- Supplier name (unnamed)
        col7 DATE,         -- Launch date (unnamed)
        col8 INTEGER       -- Stock level (unnamed)
    )
    ''')
    
    # Orders table (with mixed naming conventions)
    cursor.execute('''
    CREATE TABLE OrderData (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        OrderDate DATE,
        qty INTEGER,
        unit_price DECIMAL(10,2),
        discount_pct DECIMAL(5,2),
        sales_rep VARCHAR(100),
        region VARCHAR(50),
        FOREIGN KEY (customer_id) REFERENCES cust_tbl(id),
        FOREIGN KEY (product_id) REFERENCES prod_master(pid)
    )
    ''')
    
    # Financial data table (with cryptic names)
    cursor.execute('''
    CREATE TABLE fin_data (
        id INTEGER PRIMARY KEY,
        period DATE,
        rev DECIMAL(15,2),
        cogs DECIMAL(15,2),
        opex DECIMAL(15,2),
        mkting DECIMAL(15,2),
        misc_exp DECIMAL(15,2)
    )
    ''')
    
    # Generate sample data with quality issues
    
    # Customer data
    customer_names = ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Wilson', 'Charlie Brown', 
                     'Diana Prince', 'Eve Adams', 'Frank Miller', 'Grace Lee', 'Henry Ford']
    segments = ['Premium', 'Standard', 'Basic', 'VIP', 'Regular']
    statuses = ['Active', 'Inactive', 'Suspended', 'New', None]  # Include null values
    
    customers = []
    for i in range(1, 101):
        name = random.choice(customer_names) + f" {i}"
        email = f"customer{i}@email.com" if random.random() > 0.1 else None  # 10% missing emails
        phone = f"555-{random.randint(1000,9999)}" if random.random() > 0.15 else ""  # Some empty phones
        address = f"{random.randint(100,9999)} Main St, City {i}"
        reg_date = datetime.now() - timedelta(days=random.randint(1, 1000))
        segment = random.choice(segments)
        status = random.choice(statuses)
        
        customers.append((i, name, email, phone, address, reg_date.date(), segment, status))
    
    cursor.executemany('INSERT INTO cust_tbl VALUES (?,?,?,?,?,?,?,?)', customers)
    
    # Product data
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
    subcategories = {'Electronics': ['Phones', 'Laptops', 'Accessories'],
                    'Clothing': ['Shirts', 'Pants', 'Shoes'],
                    'Home & Garden': ['Furniture', 'Tools', 'Decor'],
                    'Sports': ['Equipment', 'Apparel', 'Accessories'],
                    'Books': ['Fiction', 'Non-Fiction', 'Educational']}
    suppliers = ['SupplierA', 'SupplierB', 'SupplierC', 'SupplierD']
    
    products = []
    for i in range(1, 51):
        cat = random.choice(categories)
        subcat = random.choice(subcategories[cat])
        price = round(random.uniform(10, 500), 2)
        cost = round(price * random.uniform(0.4, 0.8), 2)
        supplier = random.choice(suppliers)
        launch_date = datetime.now() - timedelta(days=random.randint(30, 365))
        stock = random.randint(0, 100)
        
        products.append((i, f"Product {i}", cat, subcat, price, cost, supplier, launch_date.date(), stock))
    
    cursor.executemany('INSERT INTO prod_master VALUES (?,?,?,?,?,?,?,?,?)', products)
    
    # Order data with some inconsistencies
    regions = ['North', 'South', 'East', 'West', 'Central']
    sales_reps = ['Alice Rep', 'Bob Rep', 'Charlie Rep', 'Diana Rep', 'Eve Rep']
    
    orders = []
    for i in range(1, 501):
        customer_id = random.randint(1, 100)
        product_id = random.randint(1, 50)
        order_date = datetime.now() - timedelta(days=random.randint(1, 365))
        qty = random.randint(1, 10)
        
        # Get product price (with some price variations)
        cursor.execute('SELECT price FROM prod_master WHERE pid = ?', (product_id,))
        base_price = cursor.fetchone()[0]
        unit_price = base_price * random.uniform(0.9, 1.1)  # Price variations
        
        discount = random.uniform(0, 0.3) if random.random() > 0.7 else 0
        rep = random.choice(sales_reps)
        region = random.choice(regions)
        
        orders.append((i, customer_id, product_id, order_date.date(), qty, round(unit_price, 2), 
                      round(discount * 100, 1), rep, region))
    
    cursor.executemany('INSERT INTO OrderData VALUES (?,?,?,?,?,?,?,?,?)', orders)
    
    # Financial data
    start_date = datetime(2022, 1, 1)
    financial_data = []
    
    for i in range(24):  # 24 months of data
        period = start_date + timedelta(days=30*i)
        revenue = random.uniform(100000, 500000)
        cogs = revenue * random.uniform(0.4, 0.6)
        opex = revenue * random.uniform(0.15, 0.25)
        marketing = revenue * random.uniform(0.05, 0.15)
        misc = revenue * random.uniform(0.01, 0.05)
        
        financial_data.append((i+1, period.date(), round(revenue, 2), round(cogs, 2), 
                             round(opex, 2), round(marketing, 2), round(misc, 2)))
    
    cursor.executemany('INSERT INTO fin_data VALUES (?,?,?,?,?,?,?)', financial_data)
    
    conn.commit()
    conn.close()
    
    print(f"Sample database created at: {db_path}")
    print("Database contains:")
    print("- cust_tbl: Customer data with poor column naming")
    print("- prod_master: Product data with unnamed columns (col6, col7, col8)")
    print("- OrderData: Order data with mixed naming conventions")
    print("- fin_data: Financial data with abbreviated column names")
    print("\\nData quality issues included:")
    print("- Missing values in various fields")
    print("- Inconsistent naming conventions")
    print("- Price variations")
    print("- Mixed data formats")

if __name__ == '__main__':
    create_sample_database()