# Generated by Django 2.2.11 on 2020-03-06 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('name', models.CharField(help_text='name of the product', max_length=256)),
                ('id', models.UUIDField(help_text='product id', primary_key=True, serialize=False)),
                ('category', models.CharField(help_text="product's category", max_length=256)),
            ],
        ),
    ]
