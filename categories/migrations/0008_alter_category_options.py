# Generated by Django 4.2 on 2023-04-29 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0007_alter_category_group_delete_initial_categroy"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"ordering": ["-created_at"], "verbose_name_plural": "categories"},
        ),
    ]
