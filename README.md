# Shuba Electronics & Home Appliance Shopping Management System

Web platform for browsing, ordering, and managing TVs, refrigerators, washing machines and other home appliances. Built with **Django**, **HTML/CSS**, **MySQL**, and Django authentication.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Create a MySQL database named `online_electronics`, then set `DB_USER` / `DB_PASSWORD` in `.env`.

If MySQL is not available locally, set `DB_ENGINE=sqlite` in `.env`.

```powershell
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Or simply run `.\run.bat` (or `.\run.ps1` in PowerShell).

Open http://127.0.0.1:8000/

## Demo accounts

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `prashantmhrh77@gail.com` (or `admin`) | `Prashant6969` (or `admin123`) |
| Customer | `prashant` | `prashant123` |

Admin login: `/accounts/admin-login/`  
Admin dashboard: `/dashboard/`  
Django admin backup: `/django-admin/`

The admin dashboard includes product creation, editing, deletion and inventory updates, plus
seven-day sales progress, revenue, order-status and top-product analytics. Product forms accept
JPG, PNG, WEBP and GIF uploads, show the current image while editing, and display thumbnails in
the product manager.


## Features

- Customer register/login, catalog search and filters, product details, cart, mock payment checkout, order tracking, reviews
- Admin CRUD for products/categories/brands, inventory, customers, orders/payments/delivery, review moderation, sales reports (CSV)
