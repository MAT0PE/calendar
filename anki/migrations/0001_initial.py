# Generated by Django 3.0.5 on 2021-01-02 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Vocabulary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vocab', models.TextField(default='')),
                ('meaning', models.TextField(default='')),
                ('sentence', models.TextField(blank=True)),
                ('stage', models.IntegerField(default=0)),
                ('date', models.DateField()),
            ],
        ),
    ]
