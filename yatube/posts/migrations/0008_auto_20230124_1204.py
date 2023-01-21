# Generated by Django 2.2.19 on 2023-01-24 12:04

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20230124_1203'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(('author__lt', django.db.models.expressions.F('user')), ('author__gt', django.db.models.expressions.F('user')), _connector='OR'), name='dont subscribe yourself'),
        ),
    ]
