# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-23 07:55
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.contrib.wagtailroutablepage.models
import wagtail.wagtailcore.fields

from wapps.utils import get_image_model

ImageModel = get_image_model()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0029_unicode_slugfield_dj19'),
        ('taggit', '0002_auto_20150616_2121'),
        ('wagtaildocs', '0007_merge'),
        ('wapps', '0012_identity_bg_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('intro', wagtail.wagtailcore.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtail.contrib.wagtailroutablepage.models.RoutablePageMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.wagtailcore.fields.RichTextField(verbose_name='body')),
                ('excerpt', wagtail.wagtailcore.fields.RichTextField(blank=True, help_text='Entry excerpt to be displayed on entries list. If this field is not filled, a truncate version of body text will be used.', verbose_name='excerpt')),
                ('date', models.DateTimeField(default=datetime.datetime.today, verbose_name='Post date')),
            ],
            options={
                'verbose_name': 'Blog post',
                'verbose_name_plural': 'Blog posts',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='BlogPostCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wapps.Category', verbose_name='Category')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='blogpost_categories', to='blog.BlogPost')),
            ],
        ),
        migrations.CreateModel(
            name='BlogPostRelatedLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('link_external', models.URLField(blank=True, verbose_name='External link')),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtaildocs.Document')),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Page')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_links', to='blog.BlogPost')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='BlogPostTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_items', to='blog.BlogPost')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_blogposttag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='blogpost',
            name='categories',
            field=models.ManyToManyField(blank=True, through='blog.BlogPostCategory', to='wapps.Category'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=ImageModel),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='blog.BlogPostTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
