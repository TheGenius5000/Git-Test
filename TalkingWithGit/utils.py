import git.objects
import humanize
#
# Model functions
#

# An analysis of a git object for a table entry
class TreeTableEntry:
    # Size is passed as a whole integer
    def __init__(self, git_object, latest_commit):
        self.name = git_object.name.rsplit('.', 1)
        self.is_folder = isinstance(git_object, git.objects.Tree)
        self.latest_commit_name = latest_commit.message
        self.size = humanize.naturalsize(git_object.size)
        self.date = latest_commit.committed_date

    def __str__(self):
        return f'''
Name: {self.name}
Folder: {self.is_folder}
Last commit: {self.latest_commit_name}
Size: {self.size}'''


class TreeNotFound(Exception):
    pass
