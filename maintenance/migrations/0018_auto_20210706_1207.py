# Generated by Django 3.2.4 on 2021-07-06 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0017_auto_20210511_0832'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='crtx',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='dbat',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='wipo',
        ),
        migrations.AddField(
            model_name='profile',
            name='hcmp',
            field=models.SmallIntegerField(choices=[(0, 'none'), (1, 'current'), (2, 'historical'), (3, 'all')], default=0, verbose_name='highlight competitions with entries'),
        ),
        migrations.AddField(
            model_name='profile',
            name='hnot',
            field=models.SmallIntegerField(choices=[(0, 'none'), (1, 'current WIP poem')], default=0, verbose_name='highlight note'),
        ),
        migrations.AddField(
            model_name='profile',
            name='hpom',
            field=models.SmallIntegerField(choices=[(0, 'none'), (1, 'current WIP poem'), (2, 'different from default MU')], default=0, verbose_name='highlight poem(s)'),
        ),
        migrations.AddField(
            model_name='profile',
            name='hpub',
            field=models.SmallIntegerField(choices=[(0, 'none'), (1, 'all')], default=0, verbose_name='highlight publishers with content'),
        ),
        migrations.AddField(
            model_name='profile',
            name='hsub',
            field=models.SmallIntegerField(choices=[(0, 'none'), (1, 'current'), (2, 'historical'), (3, 'all')], default=0, verbose_name='highlight magazines with submissions'),
        ),
        migrations.AddField(
            model_name='profile',
            name='scty',
            field=models.CharField(choices=[('ARG', 'Argentina'), ('AUS', 'Australia'), ('BEL', 'Belgium'), ('CAN', 'Canada'), ('DNK', 'Denmark'), ('FIN', 'Finland'), ('FRA', 'France'), ('DEU', 'Gernmany'), ('GGY', 'Gurnesey'), ('GRC', 'Greece'), ('HKG', 'Hong Kong'), ('HUN', 'Hungary'), ('ISL', 'Iceland'), ('IND', 'India'), ('IRL', 'Ireland'), ('ITA', 'Italy'), ('JPN', 'Japan'), ('JEY', 'Jersey'), ('NLD', 'Netherlands'), ('NZL', 'New Zealand'), ('NOR', 'Norway'), ('POL', 'Poland'), ('ESP', 'Spain'), ('ZAP', 'South Africa'), ('SWE', 'Sweden'), ('CHE', 'Switzerland'), ('GBR', 'UK'), ('USA', 'USA')], default='GBR', max_length=3, verbose_name='Report competitions closing in country/all'),
        ),
        migrations.AddField(
            model_name='profile',
            name='vsmg',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=True, verbose_name='Verbose system messages'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cnty',
            field=models.CharField(choices=[('ARG', 'Argentina'), ('AUS', 'Australia'), ('BEL', 'Belgium'), ('CAN', 'Canada'), ('DNK', 'Denmark'), ('FIN', 'Finland'), ('FRA', 'France'), ('DEU', 'Gernmany'), ('GGY', 'Gurnesey'), ('GRC', 'Greece'), ('HKG', 'Hong Kong'), ('HUN', 'Hungary'), ('ISL', 'Iceland'), ('IND', 'India'), ('IRL', 'Ireland'), ('ITA', 'Italy'), ('JPN', 'Japan'), ('JEY', 'Jersey'), ('NLD', 'Netherlands'), ('NZL', 'New Zealand'), ('NOR', 'Norway'), ('POL', 'Poland'), ('ESP', 'Spain'), ('ZAP', 'South Africa'), ('SWE', 'Sweden'), ('CHE', 'Switzerland'), ('GBR', 'UK'), ('USA', 'USA')], default='GBR', max_length=3, verbose_name='Country/All preference'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='dfmu',
            field=models.BooleanField(choices=[(True, 'Multiple'), (False, 'Single')], default=False, help_text='Set either single or multiple use of a poem', verbose_name='Default use'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='ftfg',
            field=models.BooleanField(default=True, verbose_name='First time flag'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='pldo',
            field=models.IntegerField(choices=[(1, 'Candidate & Used flags'), (2, 'Entries, Submissions, Publishing & Readings numbers'), (3, 'ES current & historical numbers P&R')], default=1, verbose_name='Poem listing display option'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='rbfr',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Recieve bug fix reports'),
        ),
        migrations.AlterField(
            model_name='webresource',
            name='country',
            field=models.CharField(choices=[('ARG', 'Argentina'), ('AUS', 'Australia'), ('BEL', 'Belgium'), ('CAN', 'Canada'), ('DNK', 'Denmark'), ('FIN', 'Finland'), ('FRA', 'France'), ('DEU', 'Gernmany'), ('GGY', 'Gurnesey'), ('GRC', 'Greece'), ('HKG', 'Hong Kong'), ('HUN', 'Hungary'), ('ISL', 'Iceland'), ('IND', 'India'), ('IRL', 'Ireland'), ('ITA', 'Italy'), ('JPN', 'Japan'), ('JEY', 'Jersey'), ('NLD', 'Netherlands'), ('NZL', 'New Zealand'), ('NOR', 'Norway'), ('POL', 'Poland'), ('ESP', 'Spain'), ('ZAP', 'South Africa'), ('SWE', 'Sweden'), ('CHE', 'Switzerland'), ('GBR', 'UK'), ('USA', 'USA')], default='GBR', max_length=3, verbose_name='country'),
        ),
    ]