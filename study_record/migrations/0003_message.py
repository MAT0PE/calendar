# Generated by Django 3.0.5 on 2020-12-05 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study_record', '0002_user_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.IntegerField()),
                ('receiver', models.IntegerField()),
                ('time', models.DateTimeField()),
            ],
        ),
    ]
