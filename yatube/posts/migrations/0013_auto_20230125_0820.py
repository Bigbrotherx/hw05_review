# Generated by Django 2.2.19 on 2023-01-25 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_auto_20230125_0810'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('author', 'user'), name='unique following'),
        ),
    ]
