# Generated by Django 3.1.4 on 2021-05-07 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0007_auto_20210506_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='logo',
            field=models.CharField(blank=True, help_text='UPLOADed file - must be jpg/png - max.128x128px', max_length=50, null=True, verbose_name='logo filename'),
        ),
    ]
