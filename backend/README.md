# Cartly

Cartly is a simple e-commerce store built for the CodeAlpha project using HTML, CSS, vanilla JavaScript, Django, and PostgreSQL.

## Features

- Product catalog, product detail pages, search, and category filtering
- Django user registration, login, logout, and profile page
- Session-based shopping cart
- Checkout with Cash on Delivery
- Transactional order creation and stock validation
- Order confirmation, order history, and order details
- Customer wishlists
- Product reviews and ratings with administrator moderation
- Django Admin product and order management
- PostgreSQL database
- CSRF-protected POST actions and customer order ownership checks

## Structure

- `backend/`: Django project, apps, models, API endpoints, tests, and dependencies
- `Frontend/index.html` and `Frontend/pages/`: semantic page structure, headings, forms, and page-specific content
- `Frontend/css/`: design tokens and reset (`base.css`), shared layout (`layout.css`), reusable components (`components.css`), page styling (`pages.css`), and breakpoints (`responsive.css`)
- `Frontend/js/`: app startup and shared navigation (`main.js`, `components/shell.js`), API/session handling (`api/`), reusable UI (`components/`), and page-specific data and interactions (`pages/`)
- `Frontend/assets/`: logos, illustrations, and other media
- `media/`: product images and uploaded files; Django serves these from `/media/` during local development
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

6. Open `http://127.0.0.1:8000/` for the storefront and visit `http://127.0.0.1:8000/admin/` to add products.

The storefront is static HTML and JavaScript; HTML owns the page structure, CSS owns presentation and responsive behavior, and JavaScript loads API data and handles interactions. It uses the session-authenticated JSON API under `/api/v1/`. Django redirects `/` and the legacy storefront routes to the matching files under `/static/`. When `Frontend/` is served separately (for example by VS Code Live Preview on port 3002 or Live Server on ports 5500/5501), the frontend connects to Django on the same host at port 8000. This origin is also configurable with the `?api=http://127.0.0.1:8000` query parameter, which is saved for later visits, or with `window.CARTLY_API_ORIGIN` before `main.js` loads. For a custom frontend origin, add it explicitly to `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`.

## Wishlist and reviews

Signed-in customers can add or remove products from `/wishlist/`. Each customer can submit one review per product; new and edited reviews stay hidden until an administrator approves them in Django Admin. Approved ratings are shown on product detail pages.

## Administration

Django Admin is available at `/admin/`. Staff can manage users and groups, products, orders and order items, customer wishlist entries, and product reviews. Review moderation and order status updates are also available as bulk actions. Create a staff superuser with `python manage.py createsuperuser`.

## Tests

From `Cartly/backend`, run:

```powershell
python manage.py test apps.api apps.products apps.accounts apps.cart apps.orders apps.wishlists apps.reviews
```

Tests use the database configured in settings. Ensure your PostgreSQL test database permissions are configured correctly.

## Security notes

- Do not commit `.env` or real credentials.
- Set `DEBUG=False`, a strong `SECRET_KEY`, and production `ALLOWED_HOSTS` before deployment.
- Configure HTTPS and secure cookies in production.
- This starter uses Cash on Delivery only; it does not collect or process card payments.
- Product and order data are validated on the server. Review and test the code in your environment before production use.
