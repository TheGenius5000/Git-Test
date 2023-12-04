from django.shortcuts import render
from django.http import Http404
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from .models import Notes
from.forms import WriterForm

# Create your views here.

class WriterUpdateView(UpdateView):
    model = Notes
    success_url = '/smart/writer'
    template_name = "writer/write-form.html"
class WriterCreateView(CreateView):
    model = Notes
    success_url = '/smart/writer'
    template_name = "writer/write-form.html"
    form_class = WriterForm

class WriterListView(ListView):
    model = Notes
    context_object_name = "notes"
    template_name = "writer/notes_list.html"


class WriterDetailView(DetailView):
    model = Notes
    context_object_name = "note"
