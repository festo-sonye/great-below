# Generated migration for checkout_request_id field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_deliveryconfirmation_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='checkout_request_id',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
