# CrochetShop - Handmade Crochet E-Commerce Website

## Overview
A full-featured e-commerce platform for selling handmade crochet products including bags, sweaters, tops, dolls, hats, and accessories. Built with Django and featuring a yellow (#FFD700) and green (#0A8500) theme.

## Project Structure
```
crochet_shop/          # Django project settings
shop/                  # Main shop app (products, categories, cart)
orders/                # Orders app (checkout, tracking)
templates/             # HTML templates
  base.html            # Base template with navigation
  shop/                # Shop templates
  orders/              # Order templates
static/                # Static files
  css/style.css        # Custom styling with theme colors
  js/main.js           # Cart and UI interactions
media/                 # Uploaded product images
```

## Key Features
- **Homepage**: Hero section, featured products, new arrivals, category navigation
- **Product Catalog**: Browse, filter by category/price, search functionality
- **Product Details**: Images, descriptions, color/size options, add to cart
- **Shopping Cart**: Add/remove items, quantity adjustment, subtotal calculation
- **Checkout**: Customer details form, Cash on Delivery payment
- **Order Tracking**: Unique order codes (CR-2025-XXXX), real-time status tracking
- **Admin Dashboard**: Full product and order management at /admin/

## Theme Colors
- Primary Yellow: #FFD700
- Primary Green: #0A8500
- Accent White: #FFFFFF
- Dark Text: #1A1A1A

## Admin Access
- URL: /admin/
- Username: admin
- Password: admin123

## Database
- PostgreSQL (Replit built-in)
- Models: Category, Product, ProductImage, Order, OrderItem, OrderStatusHistory

## Running the Project
The development server runs on port 5000 with Django's runserver command.

## Recent Changes
- December 2024: Initial project setup with all core features

## Next Phase Features
- Customer account registration/login
- M-PESA payment integration
- Email/SMS notifications
- Product reviews and ratings
- Sales analytics dashboard
