import json

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from projects.models import Skill

from .forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from .models import User


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                name=form.cleaned_data['name'],
                surname=form.cleaned_data['surname'],
                password=form.cleaned_data['password'],
            )
            return redirect('/users/login/')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect('/projects/list/')
            else:
                form.add_error(None, 'Неверный имейл или пароль')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('/projects/list/')


def user_detail(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user-details.html', {'user': profile_user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f'/users/{request.user.id}/')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            return redirect(f'/users/{request.user.id}/')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


def users_list(request):
    users = User.objects.all().order_by('-id')
    paginator = Paginator(users, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'users/participants.html', {
        'participants': users,
        'page_obj': page_obj,
    })


def skills_autocomplete(request):
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q).order_by('name')[:10]
    return JsonResponse([{'id': s.id, 'name': s.name} for s in skills], safe=False)


@login_required
def add_skill(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    profile_user = get_object_or_404(User, pk=user_id)
    if request.user.pk != profile_user.pk:
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

    added = not profile_user.skills.filter(pk=skill.pk).exists()
    if added:
        profile_user.skills.add(skill)

    return JsonResponse({
        'id': skill.id,
        'name': skill.name,
        'skill_id': skill.id,
        'created': created,
        'added': added,
    })


@login_required
def remove_skill(request, user_id, skill_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    profile_user = get_object_or_404(User, pk=user_id)
    if request.user.pk != profile_user.pk:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)

    if not profile_user.skills.filter(pk=skill.pk).exists():
        return JsonResponse({'error': 'Skill not in profile'}, status=400)

    profile_user.skills.remove(skill)
    return JsonResponse({'status': 'removed'})
