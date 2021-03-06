# Generated by Django 2.0.6 on 2018-06-09 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mining_main', '0005_auto_20180607_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('release_number', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='release',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mining_main.Release'),
            preserve_default=False,
        ),
    ]
