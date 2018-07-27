# Generated by Django 2.0.7 on 2018-07-27 05:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pyp', '0003_auto_20180724_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='faculty_code',
            field=models.CharField(default='CC', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='answer',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]