# Generated by Django 5.1.3 on 2024-11-28 09:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0017_teacher'),
    ]

    operations = [
        migrations.CreateModel(
            name='Man',
            fields=[
                ('person_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blog.person')),
                ('power', models.IntegerField(verbose_name='力量')),
                ('man_list', models.ManyToManyField(related_name='man_persons', to='blog.person')),
            ],
            bases=('blog.person',),
        ),
        migrations.CreateModel(
            name='Woman',
            fields=[
                ('person_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='blog.person')),
                ('beauty_degree', models.IntegerField(verbose_name='美丽度')),
                ('woman_list', models.ManyToManyField(related_name='woman_persons', to='blog.person')),
            ],
            bases=('blog.person',),
        ),
    ]