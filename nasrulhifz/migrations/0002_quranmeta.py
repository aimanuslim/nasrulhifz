# Generated by Django 2.0.2 on 2018-08-04 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nasrulhifz', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuranMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surah_number', models.CharField(max_length=10000)),
                ('ayat_number', models.CharField(max_length=10000)),
                ('ayat_string', models.CharField(max_length=10000)),
            ],
        ),
    ]