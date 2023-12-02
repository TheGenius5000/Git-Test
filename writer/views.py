from django.shortcuts import render
from django.http import Http404

from .models import Notes
# Create your views here.

def list(request):
    all_notes = Notes.objects.all()
    return render(request, 'writer/notes_list.html', {'writer': all_notes})

def detail(request, pk):
    try:
        note = Notes.objects.get(pk=pk)
    except Notes.DoesNotExist:
        raise Http404("Note doesn't exist.")
    return render(request, 'writer/notes_detail.html', {'note': note})