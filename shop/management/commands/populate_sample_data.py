from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category, Product
from orders.models import Order, OrderItem, Payment
from accounts.models import CustomUser, SellerProfile
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate database with sample crochet products and orders'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate sample data...'))

        # Create Sample Users
        users_data = [
            {
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'phone_number': '+254712345678',
                'user_type': 'customer',
            },
            {
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'phone_number': '+254723456789',
                'user_type': 'customer',
            },
            {
                'email': 'carol@example.com',
                'first_name': 'Carol',
                'last_name': 'White',
                'phone_number': '+254734567890',
                'user_type': 'customer',
            },
            {
                'email': 'david@example.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'phone_number': '+254745678901',
                'user_type': 'customer',
            },
            {
                'email': 'emily@example.com',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'phone_number': '+254756789012',
                'user_type': 'customer',
            },
            {
                'email': 'frank@example.com',
                'first_name': 'Frank',
                'last_name': 'Miller',
                'phone_number': '+254767890123',
                'user_type': 'customer',
            },
            {
                'email': 'grace@example.com',
                'first_name': 'Grace',
                'last_name': 'Lee',
                'phone_number': '+254778901234',
                'user_type': 'customer',
            },
            {
                'email': 'seller1@example.com',
                'first_name': 'Mary',
                'last_name': 'Ochieng',
                'phone_number': '+254789012345',
                'user_type': 'seller',
            },
            {
                'email': 'seller2@example.com',
                'first_name': 'Jane',
                'last_name': 'Kipchoge',
                'phone_number': '+254790123456',
                'user_type': 'seller',
            },
        ]

        users = {}
        for user_data in users_data:
            user, created = CustomUser.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'phone_number': user_data['phone_number'],
                    'user_type': user_data['user_type'],
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  ✓ Created user: {user.email} ({user.get_user_type_display()})')
            users[user_data['email']] = user

        # Create Seller Profiles
        seller_data = [
            {
                'email': 'seller1@example.com',
                'shop_name': 'Mary\'s Crochet Studio',
                'shop_description': 'Handmade crochet items with love and care. Quality products at affordable prices.',
                'phone_number': '+254789012345',
                'shop_address': '123 Nairobi Street, Nairobi, Kenya',
                'mpesa_number': '0789012345',
            },
            {
                'email': 'seller2@example.com',
                'shop_name': 'Jane\'s Creative Crafts',
                'shop_description': 'Beautiful handmade crochet designs for everyone. Custom orders welcome!',
                'phone_number': '+254790123456',
                'shop_address': '456 Kisumu Lane, Kisumu, Kenya',
                'mpesa_number': '0790123456',
            },
        ]

        for seller in seller_data:
            user = users[seller['email']]
            seller_profile, created = SellerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'shop_name': seller['shop_name'],
                    'shop_description': seller['shop_description'],
                    'phone_number': seller['phone_number'],
                    'shop_address': seller['shop_address'],
                    'mpesa_number': seller['mpesa_number'],
                    'is_verified': True,
                    'verification_date': timezone.now(),
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created seller profile: {seller_profile.shop_name}')

        # Create Categories
        categories_data = [
            {
                'name': 'Bags',
                'description': 'Beautiful handmade crochet bags and purses',
            },
            {
                'name': 'Sweaters',
                'description': 'Cozy and stylish crochet sweaters',
            },
            {
                'name': 'Tops',
                'description': 'Elegant crochet tops and crop tops',
            },
            {
                'name': 'Dolls',
                'description': 'Cute handmade amigurumi dolls',
            },
            {
                'name': 'Hats',
                'description': 'Warm and fashionable crochet hats',
            },
            {
                'name': 'Accessories',
                'description': 'Various crochet accessories and decorations',
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'  ✓ Created category: {category.name}')

        # Create Products
        products_data = [
            # Bags
            {
                'category': 'Bags',
                'name': 'Vintage Crochet Tote Bag',
                'description': 'A spacious and stylish tote bag perfect for everyday use. Handmade with soft yarn.',
                'price': '2500.00',
                'stock': 15,
                'colors': 'Beige, Brown, Black, White',
                'sizes': 'One Size',
                'featured': True,
            },
            {
                'category': 'Bags',
                'name': 'Mini Shoulder Bag',
                'description': 'Compact crochet shoulder bag for essentials. Perfect for casual outings.',
                'price': '1800.00',
                'stock': 20,
                'colors': 'Pink, Purple, Blue, Green',
                'sizes': 'One Size',
                'featured': True,
            },
            {
                'category': 'Bags',
                'name': 'Market Basket Bag',
                'description': 'Large market basket made with durable yarn. Perfect for shopping.',
                'price': '3000.00',
                'stock': 10,
                'colors': 'Natural, White, Cream',
                'sizes': 'Large, Extra Large',
            },
            # Sweaters
            {
                'category': 'Sweaters',
                'name': 'Chunky Knit Sweater',
                'description': 'Warm and cozy chunky knit sweater. Perfect for cold weather.',
                'price': '4500.00',
                'stock': 8,
                'colors': 'Gray, Navy, Black, Burgundy',
                'sizes': 'XS, S, M, L, XL',
                'featured': True,
            },
            {
                'category': 'Sweaters',
                'name': 'Crop Sweater',
                'description': 'Trendy short crochet sweater. Great for layering.',
                'price': '3500.00',
                'stock': 12,
                'colors': 'Cream, Pink, Yellow, Sage Green',
                'sizes': 'XS, S, M, L',
            },
            {
                'category': 'Sweaters',
                'name': 'Oversized Cardigan',
                'description': 'Comfortable oversized cardigan sweater. Perfect for casual wear.',
                'price': '5000.00',
                'stock': 6,
                'colors': 'White, Gray, Black, Tan',
                'sizes': 'M, L, XL, XXL',
            },
            # Tops
            {
                'category': 'Tops',
                'name': 'Halter Crop Top',
                'description': 'Stylish halter crop top. Perfect for summer.',
                'price': '2000.00',
                'stock': 18,
                'colors': 'White, Black, Gold, Silver',
                'sizes': 'XS, S, M, L',
                'featured': True,
            },
            {
                'category': 'Tops',
                'name': 'Boho Crochet Top',
                'description': 'Bohemian-style crochet top with intricate patterns.',
                'price': '2500.00',
                'stock': 14,
                'colors': 'Cream, Tan, Brown',
                'sizes': 'XS, S, M, L, XL',
            },
            {
                'category': 'Tops',
                'name': 'Summer Tank Top',
                'description': 'Lightweight crochet tank top for summer.',
                'price': '1500.00',
                'stock': 25,
                'colors': 'White, Pastel Pink, Pastel Blue, Pastel Yellow',
                'sizes': 'XS, S, M, L, XL',
            },
            # Dolls
            {
                'category': 'Dolls',
                'name': 'Amigurumi Bear',
                'description': 'Cute handmade amigurumi bear doll. Soft and cuddly.',
                'price': '800.00',
                'stock': 30,
                'colors': 'Brown, White, Pink, Blue',
                'sizes': 'Small (5in), Medium (8in)',
                'featured': True,
            },
            {
                'category': 'Dolls',
                'name': 'Amigurumi Bunny',
                'description': 'Adorable handmade bunny doll. Perfect as a toy or decoration.',
                'price': '900.00',
                'stock': 25,
                'colors': 'White, Gray, Pink',
                'sizes': 'Small (5in), Medium (8in), Large (12in)',
            },
            {
                'category': 'Dolls',
                'name': 'Crochet Octopus',
                'description': 'Fun octopus amigurumi. Great for kids.',
                'price': '1200.00',
                'stock': 12,
                'colors': 'Purple, Orange, Blue, Pink',
                'sizes': 'Medium (8in)',
            },
            # Hats
            {
                'category': 'Hats',
                'name': 'Beanie Winter Hat',
                'description': 'Warm winter beanie. Perfect for cold seasons.',
                'price': '1200.00',
                'stock': 35,
                'colors': 'Black, Gray, Navy, Red, Green',
                'sizes': 'One Size (fits most)',
                'featured': True,
            },
            {
                'category': 'Hats',
                'name': 'Summer Straw Hat',
                'description': 'Light and breathable summer hat. Perfect for beach trips.',
                'price': '1500.00',
                'stock': 20,
                'colors': 'Natural, White, Cream',
                'sizes': 'One Size (adjustable)',
            },
            {
                'category': 'Hats',
                'name': 'Pom-Pom Beanie',
                'description': 'Fun beanie with fluffy pom-pom on top.',
                'price': '1800.00',
                'stock': 16,
                'colors': 'Pink, Purple, Blue, White',
                'sizes': 'One Size',
            },
            # Accessories
            {
                'category': 'Accessories',
                'name': 'Crochet Scarf',
                'description': 'Long cozy crochet scarf. Perfect for any season.',
                'price': '1200.00',
                'stock': 22,
                'colors': 'Multicolor, Gray, Black, Cream',
                'sizes': 'One Size',
            },
            {
                'category': 'Accessories',
                'name': 'Hand Warmers',
                'description': 'Cute crochet hand warmers/mittens.',
                'price': '600.00',
                'stock': 40,
                'colors': 'White, Black, Pink, Blue',
                'sizes': 'One Size (one pair)',
            },
            {
                'category': 'Accessories',
                'name': 'Phone Cozy',
                'description': 'Soft crochet phone pouch. Fits most smartphones.',
                'price': '500.00',
                'stock': 50,
                'colors': 'Multi-color patterns available',
                'sizes': 'One Size',
            },
        ]

        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'category': categories[prod_data['category']],
                    'slug': slugify(prod_data['name']),
                    'description': prod_data['description'],
                    'price': Decimal(prod_data['price']),
                    'stock': prod_data['stock'],
                    'colors': prod_data['colors'],
                    'sizes': prod_data['sizes'],
                    'featured': prod_data.get('featured', False),
                    'available': True,
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'  ✓ Created product: {product.name} - KES {product.price}')

        # Create Sample Orders
        orders_data = [
            {
                'customer_name': 'Alice Johnson',
                'customer_phone': '+254712345678',
                'customer_email': 'alice@example.com',
                'customer_address': '123 Nairobi Street, Nairobi, Kenya',
                'status': 'delivered',
                'items': [(products[0], 1)],  # Vintage Tote Bag
            },
            {
                'customer_name': 'Bob Smith',
                'customer_phone': '+254723456789',
                'customer_email': 'bob@example.com',
                'customer_address': '456 Mombasa Road, Mombasa, Kenya',
                'status': 'on_the_way',
                'items': [(products[3], 1), (products[13], 1)],  # Chunky Sweater, Beanie
            },
            {
                'customer_name': 'Carol White',
                'customer_phone': '+254734567890',
                'customer_email': 'carol@example.com',
                'customer_address': '789 Kisumu Lane, Kisumu, Kenya',
                'status': 'packed',
                'items': [(products[6], 2), (products[9], 1)],  # Halter Top (x2), Bear Doll
            },
            {
                'customer_name': 'David Brown',
                'customer_phone': '+254745678901',
                'customer_email': 'david@example.com',
                'customer_address': '321 Nakuru Drive, Nakuru, Kenya',
                'status': 'processing',
                'items': [(products[1], 1), (products[14], 1)],  # Mini Shoulder Bag, Summer Hat
            },
            {
                'customer_name': 'Emily Davis',
                'customer_phone': '+254756789012',
                'customer_email': 'emily@example.com',
                'customer_address': '654 Eldoret Street, Eldoret, Kenya',
                'status': 'pending',
                'items': [(products[2], 1), (products[15], 1)],  # Market Basket, Pom-Pom Beanie
            },
            {
                'customer_name': 'Frank Miller',
                'customer_phone': '+254767890123',
                'customer_email': 'frank@example.com',
                'customer_address': '987 Thika Road, Thika, Kenya',
                'status': 'delivered',
                'items': [(products[10], 1)],  # Bunny Doll
            },
            {
                'customer_name': 'Grace Lee',
                'customer_phone': '+254778901234',
                'customer_email': 'grace@example.com',
                'customer_address': '246 Kasarani, Nairobi, Kenya',
                'status': 'on_the_way',
                'items': [(products[7], 1), (products[16], 1)],  # Boho Top, Scarf
            },
        ]

        for i, order_data in enumerate(orders_data):
            # Calculate total amount
            total = sum(
                products[products.index(item[0])].price * item[1]
                for item in order_data['items']
            )

            order = Order.objects.create(
                customer_name=order_data['customer_name'],
                customer_phone=order_data['customer_phone'],
                customer_email=order_data['customer_email'],
                customer_address=order_data['customer_address'],
                total_amount=total,
                status=order_data['status'],
            )

            # Create order items
            for product, quantity in order_data['items']:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=product.price,
                    quantity=quantity,
                )

            # Create Payment record with 20% deposit
            deposit = Decimal(str(total)) * Decimal('0.20')
            balance = Decimal(str(total)) * Decimal('0.80')
            
            # Determine payment status based on order status
            deposit_paid = order_data['status'] in ['processing', 'packed', 'on_the_way', 'delivered']
            balance_paid = order_data['status'] in ['on_the_way', 'delivered']
            
            payment = Payment.objects.create(
                order=order,
                deposit_amount=deposit,
                deposit_paid=deposit_paid,
                deposit_payment_method='mpesa' if deposit_paid else '',
                deposit_paid_date=timezone.now() - timedelta(days=i+1) if deposit_paid else None,
                balance_amount=balance,
                balance_paid=balance_paid,
                balance_payment_method='mpesa' if balance_paid else '',
                balance_paid_date=timezone.now() - timedelta(hours=1) if balance_paid else None,
                status='completed' if balance_paid else ('pending' if not deposit_paid else 'pending'),
            )

            # Set created_at to be in the past (for more realistic data)
            order.created_at = timezone.now() - timedelta(days=i+1)
            order.save()

            self.stdout.write(f'  ✓ Created order: {order.order_code} - {order_data["customer_name"]} (Deposit: KES {deposit}, Balance: KES {balance})')

        self.stdout.write(self.style.SUCCESS('\n✓ Sample data populated successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(categories)} categories created'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(products)} products created'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(orders_data)} orders created'))
