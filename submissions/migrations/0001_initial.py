# Generated by Django 3.1.2 on 2020-10-12 20:15

import django.db.models.deletion
import django.utils.timezone
import django_userforeignkey.models.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('collection', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Magazine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='magazine')),
                ('url', models.URLField(verbose_name='url')),
                ('access', models.CharField(choices=[('Public', 'Public'), ('Private', 'Private')], default='Public', editable=False, help_text='Magazinemags= access - default is public, alternative is private', max_length=7, verbose_name='access')),
                ('country', models.CharField(choices=[('ARG', 'Argentina'), ('AUS', 'Australia'), ('BEL', 'Belgium'), ('CAN', 'Canada'), ('DNK', 'Denmark'), ('FIN', 'Finland'), ('FRA', 'France'), ('DEU', 'Gernmany'), ('GGY', 'Gurnesey'), ('GRC', 'Greece'), ('HKG', 'Hong Kong'), ('HUN', 'Hungary'), ('ISL', 'Iceland'), ('IND', 'India'), ('IRL', 'Ireland'), ('ITA', 'Italy'), ('JPN', 'Japan'), ('JEY', 'Jersey'), ('NLD', 'Netherlands'), ('NZL', 'New Zealand'), ('NOR', 'Norway'), ('POL', 'Poland'), ('ESP', 'Spain'), ('ZAP', 'South Africa'), ('SWE', 'Sweden'), ('CHE', 'Switzerland'), ('GBR', 'UK'), ('USA', 'USA')], default='GBR', max_length=3, verbose_name='country')),
                ('noOfSubmissions', models.PositiveSmallIntegerField(default=0, verbose_name='number of submissions')),
                ('poet', django_userforeignkey.models.fields.UserForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submittedOn', models.DateField(default=django.utils.timezone.now, verbose_name='submitted on')),
                ('committedUntil', models.DateField(blank=True, help_text='Leave blank for the date to be calculated.', null=True, verbose_name='committed until')),
                ('status', models.CharField(choices=[('sbmttd', 'Submitted'), ('cnsdrd', 'Considered'), ('unknwn', 'Unknown'), ('rjctd', 'Rejected'), ('rtrnd', 'Returned'), ('wthdrn', 'Withdrawn'), ('ignrd', 'Ignored'), ('accptd', 'Accepted'), ('deletd', 'Deleted')], default='sbmttd', max_length=6, verbose_name='status')),
                ('inEdition', models.DateField(blank=True, null=True, verbose_name='in edition')),
                ('expiredOn', models.DateField(blank=True, null=True, verbose_name='expired on')),
                ('magazine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='submissions.magazine', verbose_name='magazine')),
                ('poem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collection.poem', verbose_name='poem')),
                ('poet', django_userforeignkey.models.fields.UserForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'submissions',
                'ordering': ('magazine', 'poem', 'submittedOn', 'committedUntil'),
                'unique_together': {('magazine', 'poem')},
            },
        ),
        migrations.AddField(
            model_name='magazine',
            name='submissions',
            field=models.ManyToManyField(through='submissions.Submission', to='collection.Poem'),
        ),
    ]
