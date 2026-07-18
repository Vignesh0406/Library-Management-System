# Online Bookstore System (Python Flask - Windows)

A robust, modern, and fully-featured Online Bookstore web application built with **Python (Flask)**, **SQLAlchemy**, and **Bootstrap 5**. This project provides a secure platform for customers to browse, cart, and purchase books, while offering administrators a powerful dashboard to manage inventory and fulfill orders.

## 🚀 Key Features & Architectural Improvements

This system has been migrated from a legacy Java codebase to a modern Python/Flask architecture optimized for Windows.

### 1. Advanced Authentication & Security
* **Email-Based Login:** Strict email and password authentication system.
* **Role-Based Access Control:** Distinct flows for Administrators (`usertype = 1`) and Customers (`usertype = 2`).
* **ORM Protection:** Uses SQLAlchemy ORM to prevent SQL injection and ensure data integrity.

### 2. "Glassmorphism" UI Modernization
* **Dashboard Overhaul:** Both Customer and Admin interfaces feature a premium, centered "Glassmorphism" card aesthetic.
* **Responsive Design:** Redesigned using Bootstrap 5 for professional experience on mobile and desktop.
* **Unified Navigation:** Intuitive user journey with shared base layout.

### 3. Bulletproof Order Management
* **Deterministic Order IDs:** Structured, sequenced format: `ORD<BOOK_ID>TM-<SEQUENCE>`.
* **Real-Time Status Synchronization:** Integrated Admin/Customer views for order fulfillment tracking.

### 4. Seamless Cart & Checkout
* **Cart Persistence:** Session-based cart management.
* **Inventory Deduction:** Real-time stock decrementing upon successful checkout.

---

## 🛠️ Technology Stack

* **Backend:** Python 3.x, Flask
* **Database:** SQLite (SQLAlchemy ORM)
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
* **Platform:** Windows

---

## 💻 Local Setup & Deployment (Windows)

1. **Environment Setup**:
   - Ensure **Python 3.x** is installed and added to your PATH.
   - Open a terminal in the project root.

2. **Run the Application**:
   - Simply double-click `run_local.bat` or run `python app.py`.
   - Access the application at: `http://localhost:5000`

3. **Default Admin Credentials**:
   - **Email**: `admin@bookstore.com`
   - **Password**: `admin`

---
*This project has been fully refactored from Java to Python to meet modern software engineering standards, utilizing Flask for a lightweight yet powerful full-stack experience on Windows.*
