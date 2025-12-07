from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample data for the crochet shop'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@crochetshop.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user (username: admin, password: admin123)'))

        categories_data = [
            {'name': 'Bags', 'slug': 'bags', 'description': 'Beautiful handmade crochet bags for every occasion'},
            {'name': 'Sweaters', 'slug': 'sweaters', 'description': 'Cozy crochet sweaters to keep you warm'},
            {'name': 'Tops', 'slug': 'tops', 'description': 'Stylish crochet tops for any outfit'},
            {'name': 'Dolls', 'slug': 'dolls', 'description': 'Adorable handmade crochet dolls and toys'},
            {'name': 'Hats', 'slug': 'hats', 'description': 'Trendy crochet hats and beanies'},
            {'name': 'Accessories', 'slug': 'accessories', 'description': 'Unique crochet accessories and decorations'},
        ]

        for cat_data in categories_data:
            Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'description': cat_data['description']}
            )
        self.stdout.write(self.style.SUCCESS('Created categories'))

        bags = Category.objects.get(slug='bags')
        sweaters = Category.objects.get(slug='sweaters')
        tops = Category.objects.get(slug='tops')
        dolls = Category.objects.get(slug='dolls')
        hats = Category.objects.get(slug='hats')
        accessories = Category.objects.get(slug='accessories')

        products_data = [
            {'name': 'Sunflower Tote Bag', 'slug': 'sunflower-tote-bag', 'category': bags, 'price': Decimal('2500.00'), 'stock': 5, 'description': 'A cheerful sunflower-themed tote bag perfect for summer outings. Made with soft cotton yarn in bright yellow and brown colors.', 'featured': True, 'colors': 'Yellow, Brown', 'sizes': ''},
            {'name': 'Bohemian Beach Bag', 'slug': 'bohemian-beach-bag', 'category': bags, 'price': Decimal('3200.00'), 'stock': 3, 'description': 'Large bohemian-style beach bag with fringe details. Perfect for carrying all your beach essentials.', 'featured': True, 'colors': 'Cream, Tan', 'sizes': 'Large'},
            {'name': 'Mini Crossbody Purse', 'slug': 'mini-crossbody-purse', 'category': bags, 'price': Decimal('1800.00'), 'stock': 8, 'description': 'Cute mini crossbody purse with a long strap. Perfect for carrying your phone and essentials.', 'featured': False, 'colors': 'Pink, White, Blue', 'sizes': 'Small'},
            {'name': 'Chunky Cable Sweater', 'slug': 'chunky-cable-sweater', 'category': sweaters, 'price': Decimal('4500.00'), 'stock': 4, 'description': 'Warm and cozy cable-knit style crochet sweater. Perfect for cold weather.', 'featured': True, 'colors': 'Cream, Gray, Green', 'sizes': 'S, M, L, XL'},
            {'name': 'Lightweight Cardigan', 'slug': 'lightweight-cardigan', 'category': sweaters, 'price': Decimal('3800.00'), 'stock': 6, 'description': 'Airy lightweight cardigan perfect for spring and autumn layering.', 'featured': False, 'colors': 'White, Blush, Sage', 'sizes': 'S, M, L'},
            {'name': 'Granny Square Crop Top', 'slug': 'granny-square-crop-top', 'category': tops, 'price': Decimal('2200.00'), 'stock': 7, 'description': 'Trendy granny square pattern crop top. A festival favorite!', 'featured': True, 'colors': 'Multi-color', 'sizes': 'XS, S, M, L'},
            {'name': 'Summer Halter Top', 'slug': 'summer-halter-top', 'category': tops, 'price': Decimal('1900.00'), 'stock': 10, 'description': 'Breezy halter top perfect for hot summer days. Made with soft cotton yarn.', 'featured': False, 'colors': 'White, Black, Yellow', 'sizes': 'S, M, L'},
            {'name': 'Amigurumi Bunny', 'slug': 'amigurumi-bunny', 'category': dolls, 'price': Decimal('1500.00'), 'stock': 12, 'description': 'Adorable handmade bunny doll. Safe for children of all ages.', 'featured': True, 'colors': 'Pink, Brown, Gray', 'sizes': ''},
            {'name': 'Teddy Bear Set', 'slug': 'teddy-bear-set', 'category': dolls, 'price': Decimal('2800.00'), 'stock': 5, 'description': 'Set of two matching teddy bears - perfect gift for twins or best friends.', 'featured': False, 'colors': 'Brown, Cream', 'sizes': ''},
            {'name': 'Unicorn Plushie', 'slug': 'unicorn-plushie', 'category': dolls, 'price': Decimal('2000.00'), 'stock': 8, 'description': 'Magical unicorn plushie with rainbow mane. Every little one\'s dream!', 'featured': True, 'colors': 'White with Rainbow', 'sizes': ''},
            {'name': 'Slouchy Beanie', 'slug': 'slouchy-beanie', 'category': hats, 'price': Decimal('1200.00'), 'stock': 15, 'description': 'Comfortable slouchy beanie hat for casual everyday wear.', 'featured': False, 'colors': 'Gray, Navy, Burgundy', 'sizes': 'One Size'},
            {'name': 'Summer Sun Hat', 'slug': 'summer-sun-hat', 'category': hats, 'price': Decimal('1800.00'), 'stock': 6, 'description': 'Wide-brim sun hat for beach days and garden parties.', 'featured': True, 'colors': 'Natural, White', 'sizes': 'One Size'},
            {'name': 'Coasters Set (6)', 'slug': 'coasters-set', 'category': accessories, 'price': Decimal('800.00'), 'stock': 20, 'description': 'Set of 6 colorful crochet coasters. Perfect housewarming gift!', 'featured': False, 'colors': 'Assorted', 'sizes': ''},
            {'name': 'Flower Scrunchies Pack', 'slug': 'flower-scrunchies', 'category': accessories, 'price': Decimal('500.00'), 'stock': 25, 'description': 'Pack of 3 flower-decorated crochet scrunchies.', 'featured': False, 'colors': 'Pink, Yellow, Purple', 'sizes': ''},
            {'name': 'Plant Hanger', 'slug': 'plant-hanger', 'category': accessories, 'price': Decimal('1500.00'), 'stock': 10, 'description': 'Macrame-style crochet plant hanger. Perfect for indoor plants.', 'featured': True, 'colors': 'Natural, White', 'sizes': 'Small, Medium, Large'},
        ]

        for prod_data in products_data:
            Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'name': prod_data['name'],
                    'category': prod_data['category'],
                    'price': prod_data['price'],
                    'stock': prod_data['stock'],
                    'description': prod_data['description'],
                    'featured': prod_data['featured'],
                    'colors': prod_data['colors'],
                    'sizes': prod_data['sizes'],
                    'available': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(products_data)} products'))
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
