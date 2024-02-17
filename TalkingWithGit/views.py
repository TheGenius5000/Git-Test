import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import request
from django.http.response import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.admin.utils import quote, unquote

from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView, TemplateView

from .models import Repositories
from .forms import RepositoriesForm, SwitchBranchForm, CreateBranchForm, NewFileForm, UntrackedFilesForm, \
    CommitChangesForm, UntrackedChangesForm
from .utils import *

# Create your views here.
class GitTestCreateView(CreateView):
    model = Repositories
    success_url = '/git_test/repositories'
    form_class = RepositoriesForm

    def get_form_kwargs(self):
        kwargs = super(GitTestCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        self.object.directory += f"/{self.object.id}"
        self.object.save()
        self.object.make_repo()
        return HttpResponseRedirect(self.get_success_url())


class GitTestDeleteView(DeleteView):
    model = Repositories
    success_url = '/git_test/repositories'


class GitTestUpdateView(LoginRequiredMixin, UpdateView):
    model = Repositories
    success_url = '/git_test/repositories'
    form_class = RepositoriesForm

    def get_form_kwargs(self):
        kwargs = super(GitTestUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class GitTestListView(LoginRequiredMixin, ListView):
    model = Repositories
    success_url = '/git_test/repositories'
    context_object_name = "repositories"
    login_url = "/login"

    def get_queryset(self):
        return self.request.user.repositories.all()


class GitTestDetailView(DetailView):
    model = Repositories
    context_object_name = "repository"


### Rendering git repositories

class RenderTreeView(TemplateView):
    template_name = "TalkingWithGit/repositories_folder.html"

    def get(self, request, pk, branch, relative_dir):
        print("Rendering tree...")
        if 'goback' in request.GET:
            relative_dir = relative_dir.split("|")
            if len(relative_dir) > 1:
                relative_dir = relative_dir[:-1]
            relative_dir = "|".join(relative_dir)
            return redirect('git-test.view_folder', pk=pk, branch=branch, relative_dir=relative_dir)

        trees = unquote(relative_dir)
        trees = [tree for tree in relative_dir.split("|") if tree]
        if trees[0] != "home":
            return HttpResponseBadRequest("Git directories must start with 'home'.")
        trees.pop(0)

        repository = Repositories.objects.get(pk=pk)
        print(f"Looking at {repository.directory}")

        branch_options = [(head.name, head.name) for head in repository.branches()]
        print(f"Branch Options: {branch_options}")
        print(f"{(branch, branch)}")
        new_staged_files = repository.new_files_staged(branch=branch)

        context_tree = repository.tree_table(branch=branch, path=trees)

        new_branch_form = CreateBranchForm(branches=branch_options, default=(branch, branch))
        switch_branch_form = SwitchBranchForm(branches=branch_options, default=(branch, branch))

        new_file_form = NewFileForm()
        print(repository.untracked_files())

        untracked_files_options = [(filename, filename) for filename in repository.untracked_files()]
        untracked_files_form = UntrackedFilesForm(files=untracked_files_options)
        untracked_changes_options = [(filename, filename) for filename in repository.untracked_changed_files(branch=branch)]
        print(untracked_changes_options)
        untracked_changes_form = UntrackedChangesForm(filenames=untracked_changes_options)

        commit_changes_form = CommitChangesForm()

        print(relative_dir)

        return render(request, self.template_name,
                      {'folder': context_tree,
                       'curr_directory': relative_dir,
                       'latest_commit': repository.latest_commit(branch=branch),
                       'repository': repository,
                       'branch': branch,
                       'new_branch_form': new_branch_form,
                       'switch_branch_form': switch_branch_form,
                       'new_file_form': new_file_form,
                       'untracked_changes': untracked_changes_options,
                       'untracked_files_form': untracked_files_form,
                       'untracked_changes_form': untracked_changes_form,
                       'new_staged_files': new_staged_files,
                       'commit_changes_form': commit_changes_form})

    def post(self, request, pk, branch, relative_dir):
        print(request.POST)
        repository = Repositories.objects.get(pk=pk)
        if any('branch' in key for key in request.POST):
            branch_name = request.POST['branches']
            if not repository.try_checkout(orig_branch=branch, new_branch=request.POST['branches']):
                messages.error(request,"You cannot switch branches at this time. You may have to commit changed files.")
                return HttpResponseRedirect(self.request.path_info)

            if 'branch-switch' in request.POST:
                print(f"Branch name: {branch_name}")
                return redirect('git-test.view_folder', pk=pk, branch=request.POST['branches'], relative_dir=relative_dir)
            elif 'branch-branch' in request.POST:
                print("Making a branch")
                branch_name = request.POST['new_branch']
                from_branch = request.POST['branches']
                print(branch_name, from_branch)
                try:
                    repository.new_branch_from(branch_name=branch_name, from_branch=from_branch)
                except:
                    print("Something went wrong")
                    messages.error(request, "You cannot have that branch name.")
                return redirect('git-test.view_folder', pk=pk, branch=branch_name, relative_dir=relative_dir)

        elif 'file-new' in request.POST:
            file_name_post = request.POST['filename']
            file_content = request.POST['file_content']
            if '.' not in file_name_post:
                messages.warning(request, "Your filename did not have an extension. It may become unreadable as a result.")
            dirs = relative_dir.split("|")
            path = file_name_post.split("/")
            file_name = path[-1]
            filename_dirs = path[:-1]
            print(dirs)
            print(filename_dirs)
            file_path = repository.directory+"/".join(['', *dirs[1:]])+"/".join(['', *filename_dirs])+"/"
            print(file_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file_path += file_name
            print(file_path)
            with open(file_path, mode='w+') as file:
                file.write(file_content)
            messages.success(request, f"{file_name_post} has been created.")

        elif any('files' in key for key in request.POST):
            file_names = []
            for thing in request.POST.lists():
                if thing[0] in ['files_to_add', 'changes_to_add']:
                    file_names = thing[1]
                    print(file_names)
            repository.add_untracked_files(file_names=file_names, branch=branch)
            messages.success(request, "Added files & changes to staging area.")

        elif 'commit' in request.POST:
            message = request.POST['message']
            if repository.commit(branch=branch, message=message):
                messages.success(request, "Changes were committed successfully!")


        # Default outcome (the same page)
        return HttpResponseRedirect(self.request.path_info)

class CommitHistoryView(TemplateView):
    template_name = "TalkingWithGit/repositories_commits.html"
    def get(self, request, pk, branch):
        repository = Repositories.objects.get(pk=pk)

        commits = repository.branch_commit_history(branch=branch)

        branch_options = [(head.name, head.name) for head in repository.branches()]
        print(branch_options)
        switch_branch = SwitchBranchForm(branches=branch_options)

        return render(request, self.template_name,
                      {'commits': commits,
                       'repository': repository,
                       'branch': branch})
