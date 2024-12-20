# Generated by Django 5.1.3 on 2024-11-29 06:32

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0021_publisher'),
    ]

    operations = [
        migrations.AddField(
            model_name='publisher',
            name='books',
            field=models.ManyToManyField(to='blog.book'),
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrow_date', models.DateField(default=django.utils.timezone.now)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.book')),
                ('recommended', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='club_recommended', to='blog.book', verbose_name='推荐一本书')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('teams', models.ManyToManyField(db_table='employee_teams', to='blog.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Reader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reader_name', models.CharField(max_length=50)),
                ('books', models.ManyToManyField(through='blog.Club', to='blog.book')),
            ],
        ),
        migrations.AddField(
            model_name='club',
            name='reader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.reader'),
        ),
    ]
