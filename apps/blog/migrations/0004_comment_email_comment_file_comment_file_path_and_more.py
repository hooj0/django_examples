# Generated by Django 5.1.3 on 2024-11-25 06:04

import django.db.models.functions.text
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_category_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='email',
            field=models.EmailField(default=None, help_text='邮箱地址', max_length=50, verbose_name='邮箱'),
        ),
        migrations.AddField(
            model_name='comment',
            name='file',
            field=models.FileField(blank=True, db_comment='文件', upload_to='media/files/', verbose_name='文件'),
        ),
        migrations.AddField(
            model_name='comment',
            name='file_path',
            field=models.FilePathField(blank=True, db_comment='文件路径', path='media/files/'),
        ),
        migrations.AddField(
            model_name='comment',
            name='file_size',
            field=models.BigIntegerField(db_comment='文件大小', default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='first_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='last_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='interval',
            field=models.DurationField(blank=True, help_text='Interval between comments', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='ip_address',
            field=models.GenericIPAddressField(db_comment='IP地址', default='127.0.0.1'),
        ),
        migrations.AddField(
            model_name='comment',
            name='json',
            field=models.JSONField(default=dict, verbose_name='JSON数据'),
        ),
        migrations.AddField(
            model_name='comment',
            name='photo',
            field=models.ImageField(blank=True, db_comment='头像', upload_to='media/images/'),
        ),
        migrations.AddField(
            model_name='comment',
            name='rate',
            field=models.DecimalField(decimal_places=1, max_digits=2, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='size',
            field=models.IntegerField(db_column='comment_length', db_comment='评论长度', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='stars',
            field=models.FloatField(db_comment='评分', help_text='打分', null=True, verbose_name='评分星星'),
        ),
        migrations.AddField(
            model_name='comment',
            name='uri',
            field=models.URLField(blank=True, verbose_name='URL地址'),
        ),
        migrations.AddField(
            model_name='comment',
            name='url_param',
            field=models.SlugField(null=True, verbose_name='URL路径参数'),
        ),
        migrations.AddField(
            model_name='comment',
            name='uuid',
            field=models.UUIDField(editable=False, null=True, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='pub_time',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='full_name',
            field=models.GeneratedField(db_persist=True, expression=django.db.models.functions.text.Concat('first_name', models.Value(' '), 'last_name'), output_field=models.CharField(max_length=511)),
        ),
    ]