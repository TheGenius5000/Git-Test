from django.shortcuts import render
from django.http.response import Http404, HttpResponseRedirect
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Notes
from .forms import WriterForm


# Create your views here.

class WriterDeleteView(DeleteView):
    model = Notes
    success_url = '/smart/writer'


class WriterUpdateView(UpdateView):
    model = Notes
    success_url = '/smart/writer'
    form_class = WriterForm


class WriterCreateView(CreateView):
    model = Notes
    success_url = '/smart/writer'
    form_class = WriterForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class WriterListView(LoginRequiredMixin, ListView):
    model = Notes
    context_object_name = "notes"
    template_name = "writer/notes_list.html"
    login_url = "/admin"

    def get_queryset(self):
        return self.request.user.notes.all()

class WriterDetailView(DetailView):
    model = Notes
    context_object_name = "note"
