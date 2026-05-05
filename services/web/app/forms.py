from django import forms


class ProjectSelectForm(forms.Form):
    project_id = forms.IntegerField(widget=forms.HiddenInput())


class ProjectCreateForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "New project name",
            }
        ),
    )


class ProjectUpdateForm(forms.Form):
    project_id = forms.IntegerField(widget=forms.HiddenInput())

    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Project name",
            }
        ),
    )


class ProjectDeleteForm(forms.Form):
    project_id = forms.IntegerField(widget=forms.HiddenInput())
