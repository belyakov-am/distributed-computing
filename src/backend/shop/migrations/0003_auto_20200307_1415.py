# Generated by Django 2.2.11 on 2020-03-07 14:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_auto_20200307_0637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='product id', primary_key=True, serialize=False),
        ),
    ]
