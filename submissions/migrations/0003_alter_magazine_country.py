# Generated by Django 3.2.4 on 2021-07-06 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0002_auto_20210509_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='magazine',
            name='country',
            field=models.CharField(choices=[('ARG', 'Argentina'), ('AUS', 'Australia'), ('BEL', 'Belgium'), ('CAN', 'Canada'), ('DNK', 'Denmark'), ('FIN', 'Finland'), ('FRA', 'France'), ('DEU', 'Gernmany'), ('GGY', 'Gurnesey'), ('GRC', 'Greece'), ('HKG', 'Hong Kong'), ('HUN', 'Hungary'), ('ISL', 'Iceland'), ('IND', 'India'), ('IRL', 'Ireland'), ('ITA', 'Italy'), ('JPN', 'Japan'), ('JEY', 'Jersey'), ('NLD', 'Netherlands'), ('NZL', 'New Zealand'), ('NOR', 'Norway'), ('POL', 'Poland'), ('ESP', 'Spain'), ('ZAP', 'South Africa'), ('SWE', 'Sweden'), ('CHE', 'Switzerland'), ('GBR', 'UK'), ('USA', 'USA')], default='GBR', max_length=3, verbose_name='country'),
        ),
    ]