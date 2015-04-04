# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('potluck', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(default=b'', max_length=500)),
                ('time', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('author', models.ForeignKey(related_name='author', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(related_name='subject', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='user',
        ),
        migrations.DeleteModel(
            name='Recipe',
        ),
        migrations.AlterModelOptions(
            name='saleitem',
            options={'ordering': ['expiration_date']},
        ),
        migrations.RemoveField(
            model_name='offer',
            name='location',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='time',
        ),
        migrations.RemoveField(
            model_name='saleitem',
            name='ingredient',
        ),
        migrations.DeleteModel(
            name='Ingredient',
        ),
        migrations.AddField(
            model_name='offer',
            name='item',
            field=models.ForeignKey(to='potluck.SaleItem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='saleitem',
            name='brand',
            field=models.CharField(default=b'', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='saleitem',
            name='description',
            field=models.CharField(default=b'', max_length=500, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='saleitem',
            name='name',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='saleitem',
            name='picture',
            field=models.ImageField(null=True, upload_to=b'item-pictures'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='saleitem',
            name='posted_time',
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='saleitem',
            name='purchase_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='saleitem',
            name='quantity',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userinfo',
            name='average_rating',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userinfo',
            name='num_ratings',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userinfo',
            name='total_rating',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='saleitem',
            name='expiration_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
