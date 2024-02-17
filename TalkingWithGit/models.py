from django.db import models
from django.contrib.auth.models import User

from .utils import *

from git import Repo, GitCommandError, Actor


# Create your models here.
class Repositories(models.Model):
    name = models.CharField(max_length=250)
    unique_name = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories')
    directory = models.CharField(default='D:/git_repositories', max_length=10000)
    current_branch = models.CharField(default="main", max_length=250)
    collaborators = models.ManyToManyField(User, related_name='repositories_collaborators', blank=True)

    def __str__(self):
        return self.unique_name

    # Programmatic git repo properties

    def make_repo(self):
        new_repo = Repo.init(self.directory)
        #
        # TODO: create remote url
        #
        file_name = f"{self.unique_name}.txt"
        with open(f"{self.directory}/{file_name}", "w") as f:
            f.write(f'''This is {self.name} repository. I was created so I could have a commit head for the "main" branch.
Try deleting me and seeing how that works!''')
        new_repo.index.add([file_name])
        new_repo.index.commit(message=f"Start of the commit history for {self.unique_name}", author=Actor("TalkingWithGit", "gxb199@student.bham.ac.uk"))
        return new_repo

    def new_branch_from(self, branch_name, from_branch):
        return Repo(self.directory).git.checkout("-b", branch_name, from_branch)

    def try_checkout(self, orig_branch, new_branch):
        repo = Repo(self.directory)
        try:
            repo.git.checkout(new_branch)
            repo.git.checkout(orig_branch)
        except git.exc.GitCommandError as e:
            print(e)
            return False
        return True

    def untracked_files(self):
        return Repo(self.directory).untracked_files
        # repo = Repo(self.directory)
        # untracked_strs = repo.untracked_files
        # untracked_dirs = []
        # for file in untracked_strs:
        #     untracked_dirs.append(file.split("/"))
        # return untracked_dirs

    def add_untracked_files(self, file_names, branch):
        repo = Repo(self.directory)
        repo.git.checkout(branch)
        for file_name in file_names:
            repo.git.add(file_name)

    def untracked_changed_files(self, branch):
        repo = Repo(self.directory)
        repo.git.checkout(branch)
        return [item.a_path for item in repo.index.diff(None)]

    def new_files_staged(self, branch):
        repo = Repo(self.directory)
        repo.git.checkout(branch)
        return [item.a_path for item in repo.head.commit.diff()]



    def branches(self):
        return Repo(self.directory).heads

    def top_level_directories(self):
        return Repo(self.directory).head.commit.tree.trees

    def top_level_files(self):
        return Repo(self.directory).head.commit.tree.blobs

    def active_branch(self):
        return Repo(self.directory).active_branch.name

    def latest_commit(self, branch):
        repo = Repo(self.directory)
        repo.git.checkout(branch)
        return repo.head.commit

    # This title may be misleading - a successful checkout should return emptiness, therefore it
    # will have succeeded if the function returns False
    def will_not_checkout_existing(self, branch):
        try:
            return Repo(self.directory).git.checkout(branch)
        except GitCommandError:
            return True

    # Arguments:
    #   - path: List of all trees to follow down to get to the tree - should be empty if top level.
    # Returns dictionary
    def tree_table(self, branch, path):
        repo = Repo(self.directory)
        repo.git.checkout(branch)
        curr_tree = repo.head.commit.tree
        context_tree = []
        # Tree travel according to path names
        for tree_name in path:
            for subtree in curr_tree:
                if subtree.name == tree_name:
                    curr_tree = subtree
                    break
            else:
                raise TreeNotFound(f'''Tree path improperly configured or {tree_name} did not exist
The tree path is {path}''')

        for git_object in curr_tree:
            latest_commit = next(repo.iter_commits(paths=git_object.path))
            context_tree.append(TreeTableEntry(git_object, latest_commit))

        return context_tree

    def branch_commit_history(self, branch):
        repo = Repo(self.directory)
        repo.git.checkout(branch)
        return repo.iter_commits(all=True)

    def commit(self, branch, message):
        try:
            repo = Repo(self.directory)
            repo.git.checkout(branch)
            repo.index.commit(message)
        except:
            return False
        return True
