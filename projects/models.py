from django.conf import settings
from django.db import models
from django.urls import reverse

from team_finder.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
    SKILL_NAME_MAX_LENGTH,
)


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH)

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        (PROJECT_STATUS_OPEN, 'Open'),
        (PROJECT_STATUS_CLOSED, 'Closed'),
    ]

    name = models.CharField(max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=max(len(s) for s, _ in STATUS_CHOICES),
        choices=STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_projects',
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='projects',
    )
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='favorite_projects',
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'project_id': self.pk})
