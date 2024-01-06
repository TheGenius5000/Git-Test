from django import forms
from django.core.exceptions import ValidationError

from .models import Notes


class WriterForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ('title', 'text')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control my-5'}),
            'text': forms.Textarea(attrs={'class': 'form-control mb-5'}),

        }
        labels = {
            'text': 'Write comments for commits'

        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if 'Hi Ganesh' not in title:
            raise ValidationError("You're supposed to say hi to me!")
        return title
