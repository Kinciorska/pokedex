from django import forms


class SearchPokemonForm(forms.Form):
    id_or_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))



class AddToTeamForm(forms.Form):
    is_added = forms.BooleanField(label="")


class RemoveFromTeamForm(forms.Form):
    remove = forms.BooleanField(label="")


class AddToFavouritesForm(forms.Form):
    is_added = forms.BooleanField(label="")


class RemoveFromFavouritesForm(forms.Form):
    remove = forms.BooleanField(label="")


class AddMoveForm(forms.Form):
    is_added = forms.BooleanField(label="")


class RemoveMoveForm(forms.Form):
    remove = forms.BooleanField(label="")
