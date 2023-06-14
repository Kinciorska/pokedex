from django import forms


class SearchPokemonForm(forms.Form):
    id_or_name = forms.CharField(label="Name", max_length=100)


class AddPokemonToFavourites(forms.Form):
    checked = forms.BooleanField(label="Add to favourites")
