import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm
from .models import Project, Skill


def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    all_skills = Skill.objects.order_by('name').values_list('name', flat=True)
    active_skill = request.GET.get('skill', '')
    query_prefix = f'skill={active_skill}&' if active_skill else ''

    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    paginator = Paginator(projects, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

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
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm()
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner:
        return redirect(f'/projects/{project_id}/')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
def complete_project(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    project.status = 'closed'
    project.save()
    return JsonResponse({'status': 'ok'})


@login_required
def toggle_participate(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    if user == project.owner:
        return JsonResponse({'error': 'Owner cannot leave'}, status=400)

    if project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
        participant = False
    else:
        project.participants.add(user)
        participant = True

    return JsonResponse({'status': 'ok', 'participant': participant})


@login_required
def toggle_favorite(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    if project.favorites.filter(pk=user.pk).exists():
        project.favorites.remove(user)
        favorited = False
    else:
        project.favorites.add(user)
        favorited = True

    return JsonResponse({'favorited': favorited})


@login_required
def favorite_projects(request):
    projects = request.user.favorite_projects.all().order_by('-created_at')
    return render(request, 'projects/favorite_projects.html', {'projects': projects})


def skills_autocomplete(request):
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q).order_by('name')[:10]
    return JsonResponse([{'id': s.id, 'name': s.name} for s in skills], safe=False)


@login_required
def add_project_skill(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    skill_id = data.get('skill_id')
    name = data.get('name')
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({'error': 'skill_id or name required'}, status=400)

    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)

    return JsonResponse({
        'id': skill.id,
        'name': skill.name,
        'skill_id': skill.id,
        'created': created,
        'added': added,
    })


@login_required
def remove_project_skill(request, project_id, skill_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)

    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse({'error': 'Skill not in project'}, status=400)

    project.skills.remove(skill)
    return JsonResponse({'status': 'removed'})
