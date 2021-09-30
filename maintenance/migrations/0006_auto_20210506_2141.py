# Generated by Django 3.1.4 on 2021-05-06 20:41

from django.db import migrations, models

import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0005_auto_20210506_2131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='systemparameters',
            name='logo',
        ),
        migrations.AddField(
            model_name='profile',
            name='logo',
            field=models.URLField(blank=True, help_text='Must be a dropbox link to jpg/png - max size 124x124px.  Shift-click to access', max_length=255, null=True, validators=[core.validators.dropBoxDocValidator], verbose_name='Source URL'),
        ),
    ]