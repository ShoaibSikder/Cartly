# Cartly Project Documentation

## Objective
Build a simple e-commerce store with HTML, CSS, JavaScript, Django, and PostgreSQL.

## Core features
- Product listing, detail pages, search, and category filtering
- Registration, login, logout, and profile
- Session-based shopping cart
- Cash on Delivery checkout
- Order confirmation, detail, and history
- Django Admin management

## Data model
- Product: catalog and inventory
- User: Django's built-in authentication user
- Order: customer, shipping information, status, payment method, total
- OrderItem: product snapshot, quantity, and purchase-time price

## Main flow
Browse products → add to cart → log in/register → checkout → validate stock → create order and order items in a transaction → reduce inventory → show confirmation.

## Notes
Online payment integration is not included. Configure HTTPS, secrets, allowed hosts, static files, and a production database before deployment.
