from django.test import TestCase
from .models import CustomUser, SellerProfile


class CustomUserTestCase(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            user_type='customer'
        )
        self.seller = CustomUser.objects.create_user(
            email='seller@example.com',
            password='testpass123',
            user_type='seller'
        )

    def test_user_creation(self):
        self.assertTrue(self.customer.is_customer)
        self.assertFalse(self.customer.is_seller)

    def test_seller_creation(self):
        self.assertTrue(self.seller.is_seller)
        self.assertFalse(self.seller.is_customer)
