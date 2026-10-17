# Cartly

Cartly is a simple e-commerce store built for the CodeAlpha project using HTML, CSS, vanilla JavaScript, Django, and PostgreSQL.

## Features

- Product catalog, product detail pages, search, and category filtering
- Django user registration, login, logout, and profile page
- Session-based shopping cart
- Checkout with Cash on Delivery
- Transactional order creation and stock validation
- Order confirmation, order history, and order details
- Django Admin product and order management
- PostgreSQL database
- CSRF-protected POST actions and customer order ownership checks

## Structure

- `backend/`: Django project, apps, models, views, tests, and dependencies
- `Frontend/templates/`: Django HTML templates
- `Frontend/static/`: CSS, JavaScript, images, and icons
- `docs/`: project documentation and screenshots

## Windows setup

1. Install Python and PostgreSQL.
2. Create a PostgreSQL database and user, for example:

   ```sql
   CREATE USER cartly_user WITH PASSWORD 'choose-a-strong-password';
   CREATE DATABASE cartly_db OWNER cartly_user;
   ```

3. Open a terminal in `Cartly/backend`:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

4. Edit `backend/.env` with your local PostgreSQL credentials and a secret key.
5. Run migrations and create an admin user:

   ```powershell
   python manage.py check
   python manage.py migrate
   python manage.py showmigrations products orders
   python manage.py createsuperuser
   python manage.py runserver
   ```

   `migrate` creates the database tables by applying the migrations included in the project. Confirm that the product and order migrations show `[X]` in `showmigrations`. `makemigrations` only creates migration files when you change models; it does not create database tables.

6. Open `http://127.0.0.1:8000/` and visit `http://127.0.0.1:8000/admin/` to add products.

## Tests

From `Cartly/backend`, run:

```powershell
python manage.py test apps.products apps.accounts apps.cart apps.orders
```

Tests use the database configured in settings. Ensure your PostgreSQL test database permissions are configured correctly.

## Security notes

- Do not commit `.env` or real credentials.
- Set `DEBUG=False`, a strong `SECRET_KEY`, and production `ALLOWED_HOSTS` before deployment.
- Configure HTTPS and secure cookies in production.
- This starter uses Cash on Delivery only; it does not collect or process card payments.
- Product and order data are validated on the server. Review and test the code in your environment before production use.
