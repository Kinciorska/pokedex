from django import forms


class SearchPokemonForm(forms.Form):
    id_or_name = forms.CharField(label="Name", max_length=100)


class AddToTeamForm(forms.Form):
    is_added = forms.BooleanField(label="")


class RemoveFromTeamForm(forms.Form):
    remove = forms.BooleanField(label="")


class AddToFavouritesForm(forms.Form):
    is_added = forms.BooleanField(label="")


class RemoveFromFavouritesForm(forms.Form):
    remove = forms.BooleanField(label="")