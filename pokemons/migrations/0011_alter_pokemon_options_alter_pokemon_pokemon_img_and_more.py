# Generated by Django 4.2.4 on 2024-02-15 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemons', '0010_pokemon_pokemon_entry'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pokemon',
            options={'ordering': ['pokemon_id']},
        ),
        migrations.AlterField(
            model_name='pokemon',
            name='pokemon_img',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='pokemon',
            name='pokemon_img_shiny',
            field=models.CharField(max_length=200, null=True),
        ),
    ]