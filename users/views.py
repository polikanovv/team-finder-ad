from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.service import add_skill_to_object, get_skills_autocomplete_data, paginate, remove_skill_from_object
from users.forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from users.models import User


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        User.objects.create_user(
            email=form.cleaned_data['email'],
            name=form.cleaned_data['name'],
            surname=form.cleaned_data['surname'],
            password=form.cleaned_data['password'],
        )
        return redirect('users:login')
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            return redirect('projects:list')
        form.add_error(None, 'Неверный имейл или пароль')
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('projects:list')


def user_detail(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user-details.html', {'user': profile_user})


@login_required
def edit_profile(request):
    form = EditProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('users:detail', user_id=request.user.id)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if form.is_valid():
        form.save()
        update_session_auth_hash(request, request.user)
        return redirect('users:detail', user_id=request.user.id)
    return render(request, 'users/change_password.html', {'form': form})


def users_list(request):
    users = User.objects.all().order_by('-id')
    page_obj = paginate(users, request)
    return render(request, 'users/participants.html', {
        'participants': users,
        'page_obj': page_obj,
    })


def skills_autocomplete(request):
    query = request.GET.get('q', '')
    skills = get_skills_autocomplete_data(query)
    return JsonResponse([{'id': skill.id, 'name': skill.name} for skill in skills], safe=False)


@login_required
def add_skill(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    return add_skill_to_object(request, request.user)


@login_required
def remove_skill(request, skill_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    return remove_skill_from_object(request.user, skill_id)
