from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from projects.forms import ProjectForm
from projects.models import Project, Skill
from team_finder.constants import PROJECT_STATUS_CLOSED
from team_finder.service import add_skill_to_object, get_skills_autocomplete_data, paginate, remove_skill_from_object


def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    all_skills = Skill.objects.order_by('name').values_list('name', flat=True)
    active_skill = request.GET.get('skill', '')
    query_prefix = f'skill={active_skill}&' if active_skill else ''

    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    page_obj = paginate(projects, request)

    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'page_obj': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
        'query_prefix': query_prefix,
    })


def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect('projects:detail', project_id=project.id)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner:
        return redirect('projects:detail', project_id=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect('projects:detail', project_id=project.id)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
def complete_project(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner:
        return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)

    project.status = PROJECT_STATUS_CLOSED
    project.save()
    return JsonResponse({'status': 'ok'})


@login_required
def toggle_participate(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    if user == project.owner:
        return JsonResponse({'error': 'Owner cannot leave'}, status=HTTPStatus.BAD_REQUEST)

    if participant := project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
    else:
        project.participants.add(user)

    return JsonResponse({'status': 'ok', 'participant': not participant})


@login_required
def toggle_favorite(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    if favorited := project.favorites.filter(pk=user.pk).exists():
        project.favorites.remove(user)
    else:
        project.favorites.add(user)

    return JsonResponse({'favorited': not favorited})


@login_required
def favorite_projects(request):
    projects = request.user.favorite_projects.all().order_by('-created_at')
    return render(request, 'projects/favorite_projects.html', {'projects': projects})


def skills_autocomplete(request):
    query = request.GET.get('q', '')
    skills = get_skills_autocomplete_data(query)
    return JsonResponse([{'id': skill.id, 'name': skill.name} for skill in skills], safe=False)


@login_required
def add_project_skill(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner:
        return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)

    return add_skill_to_object(request, project)


@login_required
def remove_project_skill(request, project_id, skill_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner:
        return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)

    return remove_skill_from_object(project, skill_id)
