# Generated by Django 2.1.4 on 2018-12-24 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nlp', '0002_auto_20181224_1248'),
    ]

    operations = [
        migrations.RenameField(
            model_name='redaction',
            old_name='name',
            new_name='str',
        ),
    ]