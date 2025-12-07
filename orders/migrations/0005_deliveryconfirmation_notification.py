from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0004_order_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_confirmed', models.BooleanField(default=False)),
                ('confirmed_at', models.DateTimeField(blank=True, null=True)),
                ('confirmation_note', models.TextField(blank=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_confirmation', to='orders.order')),
            ],
            options={
                'ordering': ['-confirmed_at'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('order_placed', 'Order Placed'), ('order_confirmed', 'Order Confirmed'), ('order_shipped', 'Order Shipped'), ('order_delivered', 'Order Delivered'), ('delivery_pending', 'Delivery Pending Confirmation'), ('review_request', 'Review Request'), ('message', 'New Message'), ('system', 'System Notification')], max_length=30)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='orders.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
