from django.contrib import admin
from django.contrib.auth.models import *
from django.contrib.auth.admin import UserAdmin
from .models import *


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets =  (
        (None, {'fields': ('user_type',)}),
    ) + UserAdmin.fieldsets


class ProjectAdmin(admin.ModelAdmin):
	model = Project
	list_display = ('__str__', 'lecturer', 'course')
	search_fields = ['title']

class TeamAdmin(admin.ModelAdmin):
	model = Team
	list_display = ('__str__', 'project_preference', 'course')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course)
admin.site.register(Team, TeamAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.unregister(Group)

