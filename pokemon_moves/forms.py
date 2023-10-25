from django import forms

class AddMoveForm(forms.Form):
    is_added = forms.BooleanField(label="")


class RemoveMoveForm(forms.Form):
    remove = forms.BooleanField(label="")