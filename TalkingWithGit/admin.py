from django.contrib import admin

from . import models


# Register your models here.
class TalkingWithGitAdmin(admin.ModelAdmin):
    list_display = ('unique_name',)


admin.site.register(models.Repositories, TalkingWithGitAdmin)
