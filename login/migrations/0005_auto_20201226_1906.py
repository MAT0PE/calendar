# Generated by Django 3.1.4 on 2020-12-26 10:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0004_user_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default='', max_length=20, validators=[django.core.validators.MinLengthValidator(4)]),
        ),
    ]
