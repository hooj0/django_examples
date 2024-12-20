# Generated by Django 5.1.3 on 2024-11-27 11:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_alter_choices_answer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='books',
        ),
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='blog.author', verbose_name='the related book'),
        ),
        migrations.AlterField(
            model_name='choices',
            name='answer',
            field=models.IntegerField(choices=[(None, '(Unknown)'), (0, 'No'), (1, 'Yes')], default=0, verbose_name='answer'),
        ),
    ]
