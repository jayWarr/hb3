# Generated by Django 3.1.4 on 2021-03-20 13:44

import django.db.models.deletion
import django.db.models.expressions
import django_userforeignkey.models.fields
import mptt.fields
from django.conf import settings
from django.db import migrations, models

import collection.models
import core.validators


class Migration(migrations.Migration):

    replaces = [('collection', '0001_initial'), ('collection', '0002_auto_20201014_2232'), ('collection', '0003_auto_20201021_1444'), ('collection', '0004_poeticform_reference'), ('collection', '0005_auto_20201109_1418'), ('collection', '0006_auto_20201122_1733'), ('collection', '0007_category'), ('collection', '0008_delete_category'), ('collection', '0009_category'), ('collection', '0010_auto_20210118_1539'), ('collection', '0011_auto_20210118_1541'), ('collection', '0012_auto_20210118_1545'), ('collection', '0013_categorize'), ('collection', '0014_auto_20210119_0136'), ('collection', '0015_auto_20210119_1907'), ('collection', '0016_auto_20210119_1909'), ('collection', '0017_auto_20210122_2346'), ('collection', '0018_auto_20210123_1752'), ('collection', '0019_auto_20210124_1243'), ('collection', '0020_auto_20210126_1149'), ('collection', '0021_auto_20210126_1152'), ('collection', '0022_auto_20210126_1154'), ('collection', '0023_auto_20210126_1652'), ('collection', '0024_auto_20210127_2053'), ('collection', '0025_auto_20210127_2126'), ('collection', '0026_auto_20210202_2241'), ('collection', '0027_auto_20210223_0241'), ('collection', '0028_auto_20210224_1018'), ('collection', '0029_auto_20210224_1128'), ('collection', '0030_auto_20210224_1621'), ('collection', '0031_poem_flag'), ('collection', '0032_auto_20210310_1435'), ('collection', '0033_auto_20210311_2048'), ('collection', '0034_remove_poem_flag'), ('collection', '0035_auto_20210312_0207'), ('collection', '0036_auto_20210312_0803'), ('collection', '0037_auto_20210312_0809')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PoeticForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='form')),
                ('reference', models.URLField(blank=True, max_length=255, null=True, verbose_name='reference')),
            ],
            options={
                'ordering': ([django.db.models.expressions.OrderBy(django.db.models.expressions.F('name'), nulls_first=True)],),
            },
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=80, verbose_name='Description')),
                ('document', models.FileField(upload_to=collection.models.user_directory_path, verbose_name='Titles document')),
                ('poet', django_userforeignkey.models.fields.UserForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Poem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Must be unique.  Use a _vN suffix to distinguish versions', max_length=100, verbose_name='Title')),
                ('dtlu', models.DateField(auto_now_add=True, verbose_name='Last used')),
                ('wip', models.BooleanField(default=False, help_text='Set True will automatically exclude as candidate', verbose_name='WIP')),
                ('create', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, help_text='Set to Yes to have a new, empty, source doucment automatically created & registered using the template. Leave as NO if registering an alraqdy exiting poem.', verbose_name='Create')),
                ('mu', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, help_text='Defaults to profile setting', verbose_name='Multiple use')),
                ('nE2C', models.PositiveSmallIntegerField(default=0, verbose_name='Entries')),
                ('nEE2C', models.PositiveSmallIntegerField(default=0, verbose_name='Expired entries')),
                ('nS2M', models.PositiveSmallIntegerField(default=0, verbose_name='Submissions')),
                ('nES2M', models.PositiveSmallIntegerField(default=0, verbose_name='Expired submissions')),
                ('niP', models.PositiveSmallIntegerField(default=0, verbose_name='Publications')),
                ('nR', models.PositiveSmallIntegerField(default=0, verbose_name='Readings')),
                ('sd', models.URLField(blank=True, help_text='Must be a dropbox link.  Shift-click to access', max_length=255, null=True, validators=[core.validators.dropBoxDocValidator], verbose_name='Source URL')),
                ('form', models.ForeignKey(blank=True, default=1, help_text='Can be left blank', on_delete=django.db.models.deletion.PROTECT, to='collection.poeticform', verbose_name='form')),
                ('poet', django_userforeignkey.models.fields.UserForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('cCdt', models.BooleanField(default=False, verbose_name='Currently a candidate')),
                ('hCdt', models.BooleanField(default=False, verbose_name='Historical candidate')),
                ('hbu', models.BooleanField(default=False, verbose_name='Has been used')),
                ('tag', models.CharField(blank=True, help_text='Identifying word or phrase', max_length=25, verbose_name='Tag')),
            ],
            options={
                'verbose_name': 'Poem',
                'verbose_name_plural': 'Poems',
                'unique_together': {('poet', 'title')},
            },
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('text', models.TextField(verbose_name='text')),
                ('poem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collection.poem', verbose_name='poem')),
            ],
            options={
                'ordering': ('poem', '-updated'),
            },
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('critq', 'Critique'), ('docmt', 'Document'), ('image', 'Image'), ('list', 'List'), ('note', 'Note'), ('rcdng', 'Recording'), ('refrn', 'Reference'), ('video', 'Video')], default='docmt', max_length=5, verbose_name='type')),
                ('url', models.URLField(blank=True, null=True, verbose_name='url')),
                ('poem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collection.poem', verbose_name='poem')),
                ('name', models.CharField(blank=True, max_length=30, null=True, verbose_name='name')),
            ],
            options={
                'unique_together': {('poem', 'url')},
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(blank=True, editable=False, null=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='collection.category')),
                ('count', models.PositiveSmallIntegerField(default=0, editable=False, verbose_name='count')),
                ('poet', django_userforeignkey.models.fields.UserForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'unique_together': {('name', 'parent', 'slug', 'poet')},
            },
        ),
        migrations.CreateModel(
            name='Categorize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collection.category', verbose_name='category')),
                ('poem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collection.poem', verbose_name='poem')),
                ('poet', django_userforeignkey.models.fields.UserForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('poem', 'category'),
                'unique_together': {('poet', 'poem', 'category')},
                'verbose_name_plural': 'Categorized',
            },
        ),
    ]