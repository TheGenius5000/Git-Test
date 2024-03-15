from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.utils.safestring import mark_safe
from django.contrib import messages
from djrichtextfield.widgets import RichTextWidget
from tinymce.widgets import TinyMCE

from .models import Repositories, MergeRequests
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


class MergeRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        print("kwargs:", kwargs)
        self.branches = kwargs.pop('branches', None)
        super(MergeRequestForm, self).__init__(*args, **kwargs)
        if self.branches:
            self.branch_options = [(head.name, head.name) for head in self.branches]
            self.fields['branch_source'].choices = self.branch_options
            print("Changed something!", self.fields['branch_source'])
            self.fields['branch_dest'].choices = self.branch_options
            print("Changed something!")

    branch_source = forms.ChoiceField()
    branch_dest = forms.ChoiceField()
    class Meta:
        model = MergeRequests
        fields = ('name', 'branch_source', 'branch_dest')
        labels = {
            'name': 'Name of merge request',
            'branch_source': 'Source branch to merge from',
            'branch_dest': """Destination branch (this will be the branch that recieves the source branch's changes)"""
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control my-3'}),
            'branch_source': forms.Select(),
            'branch_dest': forms.Select(),
        }

    def clean_branch_dest(self):
        branch_dest = self.cleaned_data['branch_dest']
        print(self.cleaned_data)
        if self.cleaned_data['branch_source'] == self.cleaned_data['branch_dest']:
            raise ValidationError("Failure: you cannot merge the same branch into itself.")
        return branch_dest

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

class UploadFileForm(forms.Form):
    file = forms.FileField()
    directory = forms.CharField(label="Directory name (folders separated by /, empty if current or root folder)", required=False, validators=[RegexValidator(regex="[\\/:\"*?<>|]+", inverse_match=True)])
    this_directory = forms.BooleanField(label="Start path from current directory", required=False)

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


class StashChangesForm(forms.Form):
    message = forms.CharField(label="Message")


class CommitChangesForm(forms.Form):
    message = forms.CharField(label="Message")


class FileEditForm(forms.Form):
    file = forms.CharField(initial="", label="", widget=TinyMCE())

    def __init__(self, *args, file_contents=None, **kwargs):
        super(FileEditForm, self).__init__(*args, **kwargs)
        if file_contents:
            self.fields['file'].initial = file_contents


class OtherCommitForm(forms.Form):
    other_commit = forms.ChoiceField(label="To", choices=[])

    def __init__(self, *args, choices=None, **kwargs):
        super(OtherCommitForm, self).__init__(*args, **kwargs)
        if choices:
            self.fields['other_commit'].choices = choices


class CompareBranchForm(forms.Form):
    branch1 = forms.ChoiceField(choices=[])
    branch2 = forms.ChoiceField(choices=[])

    def __init__(self, *args, choices1=None, choices2=None, default=None, **kwargs):
        super(CompareBranchForm, self).__init__(*args, **kwargs)
        if choices1:
            self.fields['branch1'].choices = choices1
            if default:
                self.fields['branch1'].initial = default
        if choices2:
            self.fields['branch2'].choices = choices2
