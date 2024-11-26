# Generated by Django 5.1.3 on 2024-11-25 07:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_comment_email_comment_file_comment_file_path_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='书名')),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='作者名称')),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='author', to='blog.category', verbose_name='related place')),
                ('tags', models.ManyToManyField(related_name='authors', to='blog.tags', verbose_name='list of sites')),
                ('books', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.book', verbose_name='the related book')),
            ],
        ),
    ]
