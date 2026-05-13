import json
from http import HTTPStatus

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from projects.models import Skill
from team_finder.constants import PAGE_SIZE, SKILLS_AUTOCOMPLETE_LIMIT


def paginate(queryset, request, page_size=PAGE_SIZE):
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(request.GET.get('page'))


def get_skills_autocomplete_data(query):
    return Skill.objects.filter(name__istartswith=query).order_by('name')[:SKILLS_AUTOCOMPLETE_LIMIT]


def add_skill_to_object(request, obj):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=HTTPStatus.BAD_REQUEST)

    skill_id = data.get('skill_id')
    name = data.get('name')
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({'error': 'skill_id or name required'}, status=HTTPStatus.BAD_REQUEST)

    added = not obj.skills.filter(pk=skill.pk).exists()
    if added:
        obj.skills.add(skill)

    return JsonResponse({
        'id': skill.id,
        'name': skill.name,
        'skill_id': skill.id,
        'created': created,
        'added': added,
    })


def remove_skill_from_object(obj, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if not obj.skills.filter(pk=skill.pk).exists():
        return JsonResponse({'error': 'Skill not found'}, status=HTTPStatus.BAD_REQUEST)
    obj.skills.remove(skill)
    return JsonResponse({'status': 'removed'})
