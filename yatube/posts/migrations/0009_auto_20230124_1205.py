# Generated by Django 2.2.19 on 2023-01-24 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20230124_1204'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='dont subscribe yourself',
        ),
    ]
