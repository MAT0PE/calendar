# Generated by Django 3.0.5 on 2020-12-22 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0002_message_read'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=9)),
                ('receiver', models.CharField(max_length=9)),
            ],
        ),
    ]
