from django.core.management.base import BaseCommand
from accounts.models import CustomUser, SellerProfile
from shop.models import Product, Category
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create Festo seller account and assign all products'

    def handle(self, *args, **options):
        # Create or get Festo seller account
        seller, created = CustomUser.objects.get_or_create(
            email='festo@example.com',
            defaults={
                'first_name': 'Festo',
                'last_name': 'Crochet',
                'user_type': 'seller',
                'phone_number': '0716567886',
                'is_verified': True,
            }
        )
        
        if created:
            seller.set_password('password123')
            seller.save()
            self.stdout.write(self.style.SUCCESS(f'Created seller: {seller.email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Seller already exists: {seller.email}'))
        
        # Create or update seller profile
        seller_profile, profile_created = SellerProfile.objects.get_or_create(
            user=seller,
            defaults={
                'shop_name': 'Festo Crochet Studio',
                'shop_description': 'Premium handmade crochet items crafted with passion and attention to detail.',
                'phone_number': '+254716567886',
                'shop_address': 'Nairobi, Kenya',
                'mpesa_number': '+254716567886',
                'bank_name': 'Kenya Commercial Bank',
                'bank_account': '1234567890',
                'is_verified': True,
            }
        )
        
        if profile_created:
            self.stdout.write(self.style.SUCCESS(f'Created seller profile: {seller_profile.shop_name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Seller profile already exists'))
        
        # Assign all products to Festo
        products = Product.objects.all()
        for product in products:
            product.seller = seller
            product.save()
        
        self.stdout.write(self.style.SUCCESS(f'Assigned {products.count()} products to {seller.get_full_name()}'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Festo Seller Account Created Successfully ==='))
        self.stdout.write(f'Email: {seller.email}')
        self.stdout.write(f'Password: password123')
        self.stdout.write(f'Phone: {seller.phone_number}')
        self.stdout.write(f'M-PESA: {seller_profile.mpesa_number}')
        self.stdout.write(f'Shop Name: {seller_profile.shop_name}')
        self.stdout.write(f'Total Products: {products.count()}')
