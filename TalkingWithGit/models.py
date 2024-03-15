from django.db import models
from django.contrib.auth.models import User

from gxb199.settings import REPOSITORIES_DIR
from .utils import *

from git import Repo, GitCommandError, Actor
from pydriller import Repository


# Create your models here.
class Repositories(models.Model):
    name = models.CharField(max_length=250)
    unique_name = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories')
    directory = models.CharField(default=REPOSITORIES_DIR, max_length=10000)
    current_branch = models.CharField(default="main", max_length=250)
    collaborators = models.ManyToManyField(User, related_name='repositories_collaborators', blank=True)

    def __str__(self):
        return self.unique_name

    # Programmatic git repo properties

    def get_repo(self, branch):
        repo = Repo(self.directory)
        repo.git.checkout(branch)
        return repo

    def make_repo(self):
        new_repo = Repo.init(self.directory)
        file_name = f"{self.unique_name}.txt"
        with open(f"{self.directory}/{file_name}", "w") as f:
            f.write(f'''This is {self.name} repository. I was created so I could have a commit head for the "main" branch.
Try deleting me and seeing how that works!''')
        new_repo.index.add([file_name])
        new_repo.index.commit(message=f"Start of the commit history for {self.unique_name}", author=Actor("TalkingWithGit", "gxb199@student.bham.ac.uk"))
        return new_repo

    def new_branch_from(self, branch_name, from_branch):
        return Repo(self.directory).git.checkout("-b", branch_name, from_branch)

    def delete_branch(self, branch):
        repo = self.get_repo(branch)
        try:
            repo.git.checkout("main")
            repo.git.branch("-D", branch)
        except git.exc.GitCommandError as e:
            print(e)
            return False
        return True


    def checkout(self, branch):
        repo = Repo(self.directory)
        try:
            repo.git.checkout(branch)
        except git.exc.GitCommandError as e:
            print(e)
            return False
        return True

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

    def add_file(self, file_name):
        repo = Repo(self.directory)
        repo.git.add(file_name)

    def add_untracked_files(self, file_names, branch):
        repo = self.get_repo(branch)
        for file_name in file_names:
            repo.git.add(file_name)

    def untracked_changed_files(self, branch):
        repo = self.get_repo(branch)
        return [item.a_path for item in repo.index.diff(None)]

    def new_files_staged(self, branch):
        repo = self.get_repo(branch)
        return [item.a_path for item in repo.head.commit.diff()]

    def diff_output(self, branch1, branch2):
        repo = self.get_repo(branch1)
        return repo.git.diff(branch1, branch2)



    def merge_test_result(self, branch1, branch2):
        repo = self.get_repo(branch1)
        repo.git.checkout(branch1)
        repo.git.checkout("-b", branch1+"test")
        try:
            output_string = repo.git.merge(branch2).format()
        except git.exc.GitCommandError as e:
            repo.git.reset("--merge")
            output_string = str(e)
        repo.git.checkout(branch1)
        repo.git.branch("-D", branch1+"test")
        return output_string

    def merge(self, branch1, branch2):
        repo = self.get_repo(branch1)
        repo.git.checkout(branch1)
        try:
            output_string = repo.git.merge(branch2).format()
        except git.exc.GitCommandError as e:
            #repo.git.reset("--merge")
            return e

        return output_string

    def stash_drop(self, branch, index):
        repo = self.get_repo(branch)
        repo.git.stash("drop", index)

    def stash_save(self, branch):
        repo = self.get_repo(branch)
        repo.git.stash("save")

    def stash_list(self, branch):
        repo = self.get_repo(branch)
        stash_table = []
        try:
            stash_output = repo.git.stash("list")
            if not stash_output:
                return stash_table
            stash_entries = stash_output.split("\n")
            stash_details = [x.split(":") for x in stash_entries]
            stash_table = [(x[0][x[0].index("{")+1:x[0].index("}")], x[1].split()[-1], x[2][1:]) for x in stash_details]
        except git.exc.GitCommandError as e:
            print(e)

        return stash_table

    def stash_apply(self, branch):
        repo = self.get_repo(branch)
        repo.git.stash("apply")

    def stash_pop(self, branch, index):
        try:
            repo = self.get_repo(branch)
            repo.git.stash("pop", index)
        except git.exc.GitCommandError as e:
            repo.git.reset("--merge")


    def stash_push(self, branch, message):
        repo = self.get_repo(branch)
        repo.git.stash("push", "-m", message)

    def branches(self):
        return Repo(self.directory).heads

    def top_level_directories(self):
        return Repo(self.directory).head.commit.tree.trees

    def top_level_files(self):
        return Repo(self.directory).head.commit.tree.blobs

    def active_branch(self):
        return Repo(self.directory).active_branch

    def latest_commit(self, branch):
        repo = self.get_repo(branch)
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
        repo = self.get_repo(branch)
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
        #repo = self.get_repo(branch)
        return Repository(self.directory, only_in_branch=branch).traverse_commits()

    def commit(self, branch, message, author_name, author_email):
        try:
            repo = self.get_repo(branch)
            repo.index.commit(message=message, author=Actor(author_name, author_email))
        except:
            return False
        return True

    def commit_message(self, commit_hash):
        return Repository(self.directory, single=commit_hash).traverse_commits()

    def commits_after_on_branch(self, branch, commit_hash):
        return Repository(self.directory, only_in_branch=branch, from_commit=commit_hash).traverse_commits()

    #INCLUSIVE with respect to the start and the end
    def changes_on_same_branch(self, branch, commit_start, commit_end):
        return Repository(self.directory,
                          only_in_branch=branch,
                          from_commit=commit_start,
                          to_commit=commit_end).traverse_commits()

    def changes_on_different_branches(self, branch1, branch2):
        repo = Repo(self.directory)
        return repo.heads[branch1].commit.diff(repo.heads[branch2].commit)

    def unmerged_files_exists(self):
        return bool(Repo(self.directory).index.unmerged_blobs())

    def unmerged_files(self):
        return list(Repo(self.directory).index.unmerged_blobs())

class MergeRequests(models.Model):
    name = models.CharField(max_length=250)
    branch_source = models.CharField(max_length=250)
    branch_dest = models.CharField(max_length=250)
    repository = models.ForeignKey(Repositories, on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)
    merge_date = models.DateField(null=True, blank=True)
    opener = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name