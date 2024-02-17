from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.utils.safestring import mark_safe

from .models import Repositories
from .models import User


class RepositoriesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(RepositoriesForm, self).__init__(*args, **kwargs)
        self.fields['collaborators'].queryset = User.objects.exclude(id=self.user.id)

    class Meta:
        model = Repositories
        fields = ('name', 'unique_name', 'collaborators')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control my-3'}),
            'unique_name': forms.TextInput(attrs={'class': 'form-control my-3'}),
            'collaborators': forms.CheckboxSelectMultiple()
        }
        labels = {
            'name': 'Enter your display name here',
            'unique_name': mark_safe('Enter your unique name for the project<br /><strong>Note: this cannot be '
                                     'changed later!</strong>'),
            'collaborators': 'Collaborators for your project'
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        return name

    def clean_unique_name(self):
        unique_name = self.cleaned_data['unique_name']
        return unique_name

    def clean_collaborators(self):
        collaborators = self.cleaned_data['collaborators']
        return collaborators


class CreateBranchForm(forms.Form):
    new_branch = forms.CharField(label="Name")
    branches = forms.ChoiceField(choices=[], label="From")

    def __init__(self, *args, branches=None, default=None, **kwargs):
        super(CreateBranchForm, self).__init__(*args, **kwargs)
        print(f"Branches are {branches}")
        if branches:
            self.fields['branches'].choices = branches
        if default:
            self.fields['branches'].initial = default


class SwitchBranchForm(forms.Form):
    branches = forms.ChoiceField(choices=[], label="From")

    def __init__(self, *args, branches=None, default=None, **kwargs):
        super(SwitchBranchForm, self).__init__(*args, **kwargs)
        print(f"Branches are {branches}")
        if branches:
            self.fields['branches'].choices = branches
        if default:
            self.fields['branches'].initial = default


class NewFileForm(forms.Form):
    filename = forms.CharField(label="File name", validators=[RegexValidator(regex="[\\/:\"*?<>|]+", inverse_match=True)])
    file_content = forms.CharField(label="File content", widget=forms.Textarea)


class UntrackedFilesForm(forms.Form):
    files_to_add = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, files=None, **kwargs):
        super(UntrackedFilesForm, self).__init__(*args, **kwargs)
        if files:
            self.fields['files_to_add'].choices = files


class UntrackedChangesForm(forms.Form):
    changes_to_add = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, filenames=None, **kwargs):
        super(UntrackedChangesForm, self).__init__(*args, **kwargs)
        if filenames:
            self.fields['changes_to_add'].choices = filenames


class CommitChangesForm(forms.Form):
    message = forms.CharField(label="Message")