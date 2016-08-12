# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-12 00:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.wagtailcore.fields

from wapps.utils import get_image_model


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0028_merge'),
        ('taggit', '0002_auto_20150616_2121'),
        ('wagtailimages', '0013_make_rendition_upload_callable'),
        ('wapps', '0006_add_identity_logo_with_custom_image_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('intro', models.TextField(blank=True, help_text='An optional introduction used as page heading and summary', null=True, verbose_name='Introduction')),
                ('body', wagtail.wagtailcore.fields.RichTextField(help_text='The main page content', verbose_name='Body')),
                ('image_full', models.BooleanField(default=False, help_text='Use the fully sized image', verbose_name='Fully sized image')),
                ('seo_type', models.CharField(choices=[('article', 'Article'), ('service', 'Service')], help_text='What does this page represents', max_length=10, verbose_name='Search engine type')),
                ('image', models.ForeignKey(blank=True, help_text='The main page image (seen when shared)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=get_image_model())),
            ],
            options={
                'verbose_name': 'Static Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StaticPageTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_items', to='wapps.StaticPage')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wapps_staticpagetag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='staticpage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='wapps.StaticPageTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]