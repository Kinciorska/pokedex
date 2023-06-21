from django import forms


class SearchPokemonForm(forms.Form):
    id_or_name = forms.CharField(label="Name", max_length=100)
