# Cartly

![Frontend](https://img.shields.io/badge/Frontend-HTML%20%7C%20CSS%20%7C%20JavaScript-blue)
![Backend](https://img.shields.io/badge/Backend-Django-0C4B33)
![API](https://img.shields.io/badge/API-Django%20REST%20Framework-red)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791)

Cartly is a full-stack e-commerce storefront for browsing products, managing a shopping cart, and placing Cash on Delivery orders. The frontend uses responsive HTML, CSS, and JavaScript; Django and Django REST Framework provide the application logic and JSON API, with PostgreSQL for persistent data.

Customers can register, browse and filter the catalog, save products to a wishlist, submit product reviews, and view their orders. Store staff manage products, inventory, orders, and review moderation through Django Admin.

## Table Of Contents

- [Screenshots](#screenshots)
- [Core Features](#core-features)
- [Customer And Staff Access](#customer-and-staff-access)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Backend Apps](#backend-apps)
- [Frontend Architecture](#frontend-architecture)
- [API Overview](#api-overview)
- [Environment Variables](#environment-variables)
- [Installation And Setup](#installation-and-setup)
- [Testing And Verification](#testing-and-verification)
- [Development Notes](#development-notes)

## Screenshots

System screenshots are stored in [`Frontend/assets/system images`](Frontend/assets/system%20images).

### Storefront

<div>
  <a href="Frontend/assets/system%20images/home%20page.png">
    <img src="Frontend/assets/system%20images/home%20page.png" width="640" alt="Cartly storefront home page" />
  </a>
</div>

### Product Catalog And Details

<div>
  <a href="Frontend/assets/system%20images/product%20overview%20page.png">
    <img src="Frontend/assets/system%20images/product%20overview%20page.png" width="640" alt="Cartly product catalog with filters and product cards" />
  </a>
  <a href="Frontend/assets/system%20images/product%20page.png">
    <img src="Frontend/assets/system%20images/product%20page.png" width="640" alt="Cartly product detail page with quantity, cart, and wishlist actions" />
  </a>
</div>

### Store Administration

<div>
  <a href="Frontend/assets/system%20images/django%20admin%20page.png">
    <img src="Frontend/assets/system%20images/django%20admin%20page.png" width="640" alt="Cartly Django Admin product management page" />
  </a>
</div>

## Core Features

### Product Discovery

- Browse active products and product categories.
- Search product names, descriptions, and categories.
- Filter by one or more categories, price range, and stock availability.
- Sort by newest, price, or rating, and browse paginated results.
- View product details, related products, stock availability, and approved reviews.

### Customer Accounts

- Register, sign in, and sign out using Django session authentication.
- View and update your account profile.
- Use authenticated customer features while retaining session and CSRF protections.

### Cart And Checkout

- Add products to a session-based cart.
- Update quantities or remove cart items.
- Validate requested quantities against current inventory.
- Place orders using Cash on Delivery.
- Recheck stock and create orders and order items in a database transaction.
- Save purchase-time product names and prices in order items.
- View your order history, confirmation, and order details.

### Wishlist And Reviews

- Save products to a personal wishlist.
- Submit or update one review per product.
- Keep new or edited reviews hidden until staff approval.
- Show approved reviews and ratings on product pages.

### Store Administration

- Manage products, categories, images, active status, and inventory.
- Review customer orders and update order statuses.
- Manage customer accounts and wishlist entries.
- Approve or reject product reviews, including through Django Admin actions.

## Customer And Staff Access

### Customers

Product browsing and product information are publicly available. Signing in is required to manage a profile, use a wishlist, submit reviews, place an order, or view your order history. Customers can only access their own profile and orders.

### Store Staff

Staff use Django Admin at `/admin/` to maintain the catalog and manage store operations. Create a staff superuser with Django's `createsuperuser` command. Administrative access is controlled by Django permissions.

## Tech Stack

### Frontend

- HTML5
- CSS with responsive layouts and reusable components
- Vanilla JavaScript with native ES modules
- Fetch API for JSON API requests
- No frontend framework or Node.js build step

### Backend

- Python
- Django 5.2
- Django REST Framework
- PostgreSQL
- `django-cors-headers`
- `python-dotenv`
- Pillow for image uploads

## Project Structure

```text
Cartly/
  backend/
    apps/
      accounts/
      api/
      cart/
      orders/
      products/
      reviews/
      wishlists/
    config/
      settings.py
      urls.py
      asgi.py
      wsgi.py
    manage.py
    requirements.txt
    .env.example

  Frontend/
    assets/
      system images/
    css/
      base.css
      layout.css
      components.css
      pages.css
      responsive.css
    js/
      api/
      components/
      pages/
      accounts.js
      config.js
      main.js
      quantity.js
    pages/

  docs/
    project-documentation.md
  media/
  README.md
```

## Backend Apps

### `api`

Provides the session-authenticated JSON API for accounts, product browsing, cart operations, wishlists, reviews, and orders. It also contains shared API serializers and request middleware.

### `accounts`

Handles registration, sign-in/sign-out, profile editing, and account-related pages.

### `products`

Defines the product catalog and inventory, catalog pages, product images, category navigation, and product administration.

### `cart`

Manages a session-based cart, item quantities, stock checks, and cart pages.

### `orders`

Creates orders and purchase-time order items, validates checkout, tracks order status, and provides customer order history and administration.

### `wishlists`

Stores each customer's saved products and provides wishlist pages and controls.

### `reviews`

Stores product ratings and review text, prevents duplicate customer reviews for a product, and supports staff moderation.

## Frontend Architecture

### `Frontend/index.html` and `Frontend/pages`

Static page structure for the storefront and customer flows: catalog, product detail, cart, checkout, order history, order confirmation, profile, wishlist, and reviews.

### `Frontend/js/main.js`

Starts the frontend application, initializes shared navigation, and loads page-specific interactions.

### `Frontend/js/config.js` and `Frontend/js/api`

Configure the API origin and provide shared request handling plus domain API modules for accounts, catalog, cart, orders, and wishlists.

### `Frontend/js/components`

Reusable storefront shell and product-card components.

### `Frontend/js/pages`

Page-specific behavior for the home page, catalog, customer accounts, commerce flows, and community-related features such as reviews and wishlists.

### `Frontend/css`

Base styles, layout, reusable components, page presentation, and responsive breakpoints.

## API Overview

Base API URL:

```text
http://127.0.0.1:8000/api/v1/
```

The API uses Django session authentication. Requests that change state must send a valid CSRF token.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/csrf/` | Obtain a CSRF token |
| `POST` | `/auth/register/` | Register a customer |
| `POST` | `/auth/login/` | Sign in |
| `POST` | `/auth/logout/` | Sign out |
| `GET` | `/auth/me/` | Get the current account |
| `GET`, `PATCH` | `/auth/profile/` | View or update your profile |
| `GET` | `/home/` | Load featured products, categories, and product collections |
| `GET` | `/products/` | Search, filter, sort, and paginate active products |
| `GET` | `/products/<slug>/` | Get product details and related products |
| `GET`, `POST` | `/products/<slug>/reviews/` | List approved reviews or submit/update your review |
| `GET` | `/cart/` | Get the current session cart |
| `POST`, `PUT`, `DELETE` | `/cart/items/<product_id>/` | Add, update, or remove a cart item |
| `GET` | `/wishlist/` | Get the signed-in customer's wishlist |
| `POST`, `DELETE` | `/wishlist/items/<product_id>/` | Save or remove a product |
| `GET`, `POST` | `/orders/` | List your orders or submit a checkout |
| `GET` | `/orders/<order_id>/` | Get one of your orders |

Product catalog query parameters include `q`, repeated `category` values, `min`, `max`, `stock=1`, `sort` (`newest`, `price-asc`, `price-desc`, or `rating`), and `page`.

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and set the local PostgreSQL database connection and Django settings:

```env
SECRET_KEY=replace-with-a-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=cartly_db
DB_USER=cartly_user
DB_PASSWORD=replace-with-your-database-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

Keep `.env` and real credentials out of version control. For production, set `DEBUG=False`, use a strong secret key and explicit allowed hosts, configure HTTPS and secure cookies, and serve static and uploaded media appropriately.

The frontend uses Django on the same host at port `8000` by default. To use a different backend, open the frontend with `?api=http://127.0.0.1:8000`; the selected API origin is saved in the browser. When serving the frontend from another origin, configure `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` for that origin.

## Installation And Setup

### Prerequisites

- Python and pip
- PostgreSQL
- A modern web browser

### Database Setup

Create a PostgreSQL role and database, for example:

```sql
CREATE USER cartly_user WITH PASSWORD 'choose-a-strong-password';
CREATE DATABASE cartly_db OWNER cartly_user;
```

Use your own local credentials in `backend/.env`.

### Backend Setup

In PowerShell, from the repository root:

```powershell
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`, then apply the checked-in migrations and create a staff account:

```powershell
python manage.py check
python manage.py migrate
python manage.py showmigrations products orders
python manage.py createsuperuser
python manage.py runserver
```

The storefront is available at `http://127.0.0.1:8000/`; Django Admin is at `http://127.0.0.1:8000/admin/`. Add or manage catalog products in Django Admin.

### Frontend Setup

Django serves the static frontend during local development. If you serve `Frontend/` separately using a local static server or editor preview, keep Django running and configure the API origin and matching CORS/CSRF trusted origins.

## Testing And Verification

From `backend/`, with the virtual environment active and database settings configured, run:

```powershell
python manage.py check
python manage.py test apps.api apps.products apps.accounts apps.cart apps.orders apps.wishlists apps.reviews
```

The tests use the database configured in Django settings. Ensure your PostgreSQL test database permissions are set up correctly.

## Development Notes

- The frontend is static HTML, CSS, and JavaScript; Django supplies data through the session-authenticated `/api/v1/` endpoints.
- Product, cart, wishlist, review, and order data are served by the backend rather than being hard-coded into the UI.
- Cart contents are session-based. Wishlists and orders are tied to the signed-in customer.
- Checkout validates the cart and stock again on the server, creates the order transactionally, and then reduces inventory.
- The supported payment method is Cash on Delivery. Online card processing is not included.
- Customer reviews are visible publicly only after staff approval.
- Apply checked-in database migrations with `migrate`. `makemigrations` is for creating migration files after model changes, not for initializing a database.
- Product images and other uploaded files are stored under `media/` during local development. Configure suitable protected media storage and serving for production.
- Screenshots in the README are design/system references. Storefront products and customer data are managed through the database and backend.
