# Generated by Django 4.0.4 on 2022-06-06 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_alter_author_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'permissions': (('can_edit_books', 'May create, edit and delete books.'),)},
        ),
    ]
