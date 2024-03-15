import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import request
from django.http.response import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.admin.utils import quote, unquote
from django.urls import reverse
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView, TemplateView

from .models import Repositories, MergeRequests
from .forms import *
from .utils import *
from .templatetags.utils import *

# Create your views here.

### Generic Views for repository object
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


### Merge Request Views
class GitTestMergeRequestCreateView(LoginRequiredMixin, CreateView):
    model = MergeRequests
    success_url = '/git_test/repositories'
    form_class = MergeRequestForm

    def get_form_kwargs(self):
        kwargs = super(GitTestMergeRequestCreateView, self).get_form_kwargs()
        repository = Repositories.objects.get(pk=self.kwargs.get('repo_pk'))
        kwargs['branches'] = repository.branches()
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.repository = Repositories.objects.get(pk=self.kwargs.get('repo_pk'))
        self.object.opener = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class GitTestMergeRequestDetailView(TemplateView):
    template_name = "TalkingWithGit/mergerequests_detail.html"

    def get(self, request, repo_pk, pk):
        repository = Repositories.objects.get(pk=repo_pk)
        merge_request = MergeRequests.objects.get(pk=pk)
        context = {'repository': repository, 'merge_request': merge_request, 'diff': ''}
        if 'trymerge' in request.GET:
            context['diff'] = repository.merge_test_result(merge_request.branch_source,
                                                           merge_request.branch_dest).format()
        return render(request, self.template_name, context)

    def post(self, request, repo_pk, pk):
        if 'merge' in request.POST:
            repository = Repositories.objects.get(pk=repo_pk)
            merge_request = MergeRequests.objects.get(pk=pk)
            if isinstance(repository.merge(merge_request.branch_dest, merge_request.branch_source), git.exc.GitCommandError):
                messages.warning(request, "There is conflicts that you need to resolve in order to finish the merge.")
            else:
                messages.success(request, "The merge went ahead successfully, there were no conflicts!")
            merge_request.closed = True
            merge_request.merge_date = datetime.now()
            merge_request.save()
        return HttpResponseRedirect(self.request.path_info)


class GitTestMergeRequestDeleteView(DeleteView):
    model = MergeRequests
    context_object_name = "merge_request"
    def get_success_url(self):
        return reverse("git-test.detail", kwargs={"pk": self.kwargs.get("repo_pk")})

class GitTestMergeRequestHistoryView(TemplateView):
    template_name = "TalkingWithGit/mergerequests_list.html"

    def get(self, request, pk):
        previous_merge_requests = MergeRequests.objects.filter(closed=True, repository=pk)
        repository = Repositories.objects.get(pk=pk)
        print(repository.name)
        return render(request, self.template_name, {
            'previous_merge_requests': previous_merge_requests,
            'repository': repository,
        })

### Rendering git repositories

class RenderTreeView(TemplateView):
    template_name = "TalkingWithGit/repositories_folder.html"

    def get(self, request, pk, branch, relative_dir):
        print("Rendering tree...")
        print(request.GET)
        if 'goback' in request.GET:
            relative_dir = relative_dir.split("|")
            if len(relative_dir) > 1:
                relative_dir = relative_dir[:-1]
            relative_dir = "|".join(relative_dir)
            return redirect('git-test.view_folder', pk=pk, branch=branch, relative_dir=relative_dir)

        repository = Repositories.objects.get(pk=pk)
        #This guard acts against merge conflict errors.
        if repository.unmerged_files_exists():
            return redirect('git-test.resolve_merge_conflict', pk=pk)
        print(f"Looking at {repository.directory}")

        headless = 'headless' in request.GET

        trees = unquote(relative_dir)
        trees = [tree for tree in relative_dir.split("|") if tree]
        #Guard against malformed directories
        if trees[0] != "home":
            return HttpResponseBadRequest("Git directories must start with 'home'.")
        trees.pop(0)


        branch_options = [(head.name, head.name) for head in repository.branches()]
        print(f"Branch Options: {branch_options}")
        print(f"{(branch, branch)}")
        new_staged_files = repository.new_files_staged(branch=branch)

        context_tree = repository.tree_table(branch=branch, path=trees)

        if headless:
            new_branch_form = CreateBranchForm(branches=[(branch, branch)],  default=(branch, branch))
        else:
            new_branch_form = CreateBranchForm(branches=branch_options, default=(branch, branch))
        switch_branch_form = SwitchBranchForm(branches=branch_options, default=(branch, branch))
        compare_branch_form = CompareBranchForm(choices1=branch_options, choices2=branch_options, default=(branch, branch))

        merge_requests = MergeRequests.objects.filter(closed=False, repository=repository.id)

        new_file_form = NewFileForm()
        upload_file_form = UploadFileForm()
        print(repository.untracked_files())

        untracked_files_options = [(filename, mark_safe(f"<a href={filepath_to_url(filename)}>{filename}</a>")) for filename in repository.untracked_files()]
        untracked_files_form = UntrackedFilesForm(files=untracked_files_options)
        untracked_changes_options = [(filename, mark_safe(f"<a href={filepath_to_url(filename)}>{filename}</a>")) for filename in repository.untracked_changed_files(branch=branch)]
        print(untracked_changes_options)
        untracked_changes_form = UntrackedChangesForm(filenames=untracked_changes_options)

        stash_changes_form = StashChangesForm()
        commit_changes_form = CommitChangesForm()

        print(relative_dir)

        stash_data = repository.stash_list(branch=branch)

        commit_message = next(repository.commit_message(commit_hash=branch)).msg

        return render(request, self.template_name,
                      {'folder': context_tree,
                       'curr_directory': relative_dir,
                       'latest_commit': repository.latest_commit(branch=branch),
                       'repository': repository,
                       'branch': branch,
                       'new_branch_form': new_branch_form,
                       'switch_branch_form': switch_branch_form,
                       'compare_branch_form': compare_branch_form,
                       'merge_requests': merge_requests,
                       'new_file_form': new_file_form,
                       'upload_file_form': upload_file_form,
                       'untracked_changes': untracked_changes_options,
                       'untracked_files_form': untracked_files_form,
                       'untracked_changes_form': untracked_changes_form,
                       'new_staged_files': new_staged_files,
                       'stash_changes_form': stash_changes_form,
                       'commit_changes_form': commit_changes_form,
                       'stash_data': stash_data,
                       'headless': headless,
                       'commit_message': commit_message})

    def post(self, request, pk, branch, relative_dir):
        print(request.POST)
        repository = Repositories.objects.get(pk=pk)

        if any('branch' in key for key in request.POST):
            if 'delete-branch' in request.POST:
                if branch == "main":
                    messages.error(request, 'You cannot delete the main branch.')
                    return HttpResponseRedirect(self.request.path_info)
                if repository.delete_branch(branch=branch):
                    messages.success(request, f"Branch '{branch}' was deleted successfully.")
                    return redirect('git-test.view_folder', pk=repository.id, branch='main', relative_dir='home')
                else:
                    messages.error(request, f"Branch '{branch}' couldn't be deleted.")
                    return HttpResponseRedirect(self.request.path_info)

            if 'branch-compare' in request.POST:
                return redirect('git-test.compare_branches', pk=pk, branch1=request.POST['branch1'], branch2=request.POST['branch2'])

            branch_name = request.POST['branches']
            if not repository.try_checkout(orig_branch=branch, new_branch=request.POST['branches']):
                messages.error(request,"You cannot switch branches at this time. You may have to commit changed files otherwise the changes will be lost.")
                return HttpResponseRedirect(self.request.path_info)

            if 'branch-switch' in request.POST:
                print(f"Branch name: {branch_name}")
                return redirect('git-test.view_folder', pk=pk, branch=request.POST['branches'], relative_dir=relative_dir)
            elif 'branch-branch' in request.POST:
                print("Making a branch")
                branch_name = request.POST['new_branch']
                from_branch = request.POST['branches']
                print(branch_name, from_branch)
                if 'test' in branch_name:
                    messages.error(request, "We do not allow for 'test' to exist in the branch name.")
                else:
                    try:
                        repository.new_branch_from(branch_name=branch_name, from_branch=from_branch)
                        return redirect('git-test.view_folder', pk=pk, branch=branch_name, relative_dir=relative_dir)
                    except:
                        print("Something went wrong")
                        messages.error(request, "You cannot have that branch name.")
                        branch_name = from_branch
                return redirect('git-test.view_folder', pk=pk, branch=branch, relative_dir=relative_dir)


        elif any('stash' in (stash_command := key) for key in request.POST):
            stash_command = stash_command.split("-")
            if "apply" == stash_command[1]:
                repository.stash_pop(branch=branch, index=stash_command[2])
                messages.success(request, f"Stash {stash_command[0]} was applied successfully.")
            elif "drop" == stash_command[1]:
                repository.stash_drop(branch=branch, index=stash_command[2])
                messages.success(request, f"Stash {stash_command[0]} was dropped successfully.")
            elif "save" == stash_command[1]:
                stash_message = request.POST["message"]
                repository.stash_push(branch=branch, message=stash_message)
                messages.success(request, f"""Stash was saved successfully with message "{stash_message}".""")

        elif 'file-new' in request.POST:
            file_name_post = request.POST['filename']
            file_content = request.POST['file_content']
            if '.' not in file_name_post:
                messages.warning(request, "Your filename did not have an extension. It may become unreadable as a result.")
            if '|' in file_name_post:
                messages.error(request, "You cannot create a file with '|' in the name.")
            else:
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
                with open(file_path, mode='w+') as file:
                    file.write(file_content)
                messages.success(request, f"{file_name_post} has been created.")

        elif 'file-upload' in request.POST:
            new_file = request.FILES['file']
            path_string = repository.directory+"/"
            if 'this_directory' in request.POST:
                print("You chose this directory!")
                dirs = relative_dir.split("|")[1:]
                print(dirs)
                for dir in dirs:
                    path_string += dir+"/"
                    print(path_string)

            for dir in request.POST['directory'].split("/"):
                path_string += dir+"/"
            path_string += new_file.name
            print(path_string)
            os.makedirs(os.path.dirname(path_string), exist_ok=True)
            with open(path_string, mode='wb+') as file:
                for chunk in new_file.chunks():
                    file.write(chunk)

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
            if request.user.is_anonymous:
                username = "Anonymous"
                email = "N/A"
            else:
                username = self.request.user.username
                email = self.request.user.email
            if repository.commit(branch=branch, message=message, author_name=username, author_email=email):
                messages.success(request, "Changes were committed successfully!")
            else:
                messages.error(request, "The file didn't commit for some reason.")



        # Default outcome (the same page)
        return HttpResponseRedirect(self.request.path_info)

class CommitHistoryView(TemplateView):
    template_name = "TalkingWithGit/repositories_commits.html"
    def get(self, request, pk, branch):
        repository = Repositories.objects.get(pk=pk)

        commits = repository.branch_commit_history(branch=branch)

        branch_options = [(head.name, head.name) for head in repository.branches()]
        print(branch_options)
        switch_branch_form = SwitchBranchForm(branches=branch_options, default=(branch, branch))


        return render(request, self.template_name,
                      {'commits': commits,
                       'repository': repository,
                       'branch': branch,
                       'switch_branch_form': switch_branch_form})


    def post(self, request, pk, branch):
        repository = Repositories.objects.get(pk=pk)
        if 'branch-switch' in request.POST:
            branch_name = request.POST['branch-switch']
            print(f"Branch name: {branch_name}")
            return redirect('git-test.view_commit_history', pk=pk, branch=request.POST['branches'])

        # Default outcome (the same page)
        return HttpResponseRedirect(self.request.path_info)

class EditFileView(TemplateView):
    template_name = "TalkingWithGit/repositories_edit_file.html"

    def get(self, request, pk, branch, relative_dir, filename,  *args, **kwargs):
        repository = Repositories.objects.get(id=pk)
        print(request.GET)
        if not repository.checkout(branch) and 'nocheckout' not in request.GET:
            messages.error("Something went really bad. Could not switch branch.")
            return redirect('git-test.detail', pk=pk)
        dir_as_string = relative_dir.replace("|", "/").replace("home", "")
        path_to_file = f"{repository.directory}{dir_as_string}/{filename}"
        print(path_to_file)
        print(os.path.exists(path_to_file))
        if os.path.exists(path_to_file):
            with open(path_to_file, "r") as f:
                file_contents = f.read()
        else:
            file_contents = "New File"
        file_edit_form = FileEditForm(file_contents=file_contents)
        return render(request, self.template_name, {
            "repository": repository,
            "relative_dir": relative_dir,
            "dir_as_string": dir_as_string,
            "file_edit_form": file_edit_form,
            "branch": branch,
            "filename": filename,
            "nocheckout": 'nocheckout' in request.GET,
        })

    def post(self, request, branch, pk, relative_dir, filename,  *args, **kwargs):
        print(request.POST)
        repository = Repositories.objects.get(id=pk)
        dir_as_string = relative_dir.replace("|", "/").replace("home", "")
        path_to_file = f"{repository.directory}/{dir_as_string}/{filename}"
        print(path_to_file)
        if 'edit-save' in request.POST:
            file_contents = request.POST['file']
            if not os.path.exists(path_to_file):
                os.makedirs(path_to_file)
            with open(path_to_file, mode="w+") as file:
                file.write(file_contents)
        elif 'edit-delete' in request.POST:
            os.remove(path_to_file)

        return redirect('git-test.view_folder', pk=pk, branch=branch, relative_dir=relative_dir)


class SelectCommitCompareView(TemplateView):
    template_name = 'TalkingWithGit/repositories_compare_select.html'
    def get(self, request, pk, branch, commit1hash, *args, **kwargs):
        print(request.GET)
        repository = Repositories.objects.get(id=pk)
        commits_from_hash = list(repository.commits_after_on_branch(branch=branch, commit_hash=commit1hash))
        commit1_message = commits_from_hash[0].msg
        commit_options = ((commit.hash, commit.msg) for commit in commits_from_hash[1:])
        commit2_form = OtherCommitForm(choices=commit_options)
        return render(request, self.template_name, {
            'repository': repository,
            'commit2_form': commit2_form,
            'commit1_message': commit1_message,
            'commits_after_hash': commits_from_hash[1:],
        })

    def post(self, request, pk, branch, commit1hash, *args, **kwargs):
        print(request.POST)

        return redirect('git-test.compare_commit_same_branch', pk=pk, branch=branch, commit1hash=commit1hash, commit2hash=request.POST['other_commit'])


class CompareCommitSameBranchView(TemplateView):
    template_name = 'TalkingWithGit/repositories_compare_commits.html'

    def get(self, request, pk, branch, commit1hash, commit2hash, *args, **kwargs):
        repository = Repositories.objects.get(id=pk)
        commits = list(repository.changes_on_same_branch(branch=branch, commit_start=commit1hash, commit_end=commit2hash))
        print([commit.msg for commit in commits])
        return render(request, self.template_name, {
            'repository': repository,
            'branch': branch,
            'commits':commits,
        })


class ResolveMergeConflictView(TemplateView):
    template_name = "TalkingWithGit/repositories_merge_conflict.html"

    def get(self, request, pk, *args, **kwargs):
        repository = Repositories.objects.get(id=pk)
        if repository.unmerged_files_exists():
            unmerged_files = repository.unmerged_files()
            return render(request, self.template_name, {
                'repository': repository,
                'unmerged_files': unmerged_files,
            })
        else:
            return redirect('git-test.view_folder', pk=pk, branch=repository.active_branch().name, relative_dir='home')

    def post(self, request, pk, *args, **kwargs):
        print(request.POST)
        repository = Repositories.objects.get(id=pk)
        for key, value in request.POST.items():
            if 'unmerged_file' in key:
                repository.add_file(value)
        return HttpResponseRedirect(self.request.path_info)


class CompareBranchesView(TemplateView):
    template_name = "TalkingWithGit/repositories_compare_branches.html"

    def get(self, request, pk, branch1, branch2, *args, **kwargs):
        repository = Repositories.objects.get(id=pk)
        diffs = repository.changes_on_different_branches(branch1, branch2)
        print(request.GET)
        print("Help!")
        return render(request, self.template_name, {
            'diffs': diffs,
            'repository': repository,
            'branch1': branch1,
            'branch2': branch2,
        })