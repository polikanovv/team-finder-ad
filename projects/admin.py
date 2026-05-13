from django.contrib import admin

from projects.models import Project, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'get_skills', 'get_participants_count', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    search_fields = ['name', 'description']

    def get_skills(self, obj):
        return ', '.join(obj.skills.values_list('name', flat=True))
    get_skills.short_description = 'Навыки'

    def get_participants_count(self, obj):
        return obj.participants.count()
    get_participants_count.short_description = 'Участники'
