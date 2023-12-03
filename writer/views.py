from django.shortcuts import render
from django.http import Http404
from django.views.generic import ListView, DetailView

from .models import Notes


# Create your views here.

class WriterListView(ListView):
    model = Notes
    context_object_name = "notes"
    template_name = "writer/notes_list.html"


class WriterDetailView(DetailView):
    model = Notes
    context_object_name = "note"
