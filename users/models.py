import io
import random

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw

from team_finder.constants import (
    ABOUT_MAX_LENGTH,
    AVATAR_COLORS,
    AVATAR_FONT_SIZE,
    AVATAR_SIZE,
    AVATAR_TEXT_ANCHOR,
    AVATAR_TEXT_COLOR,
    PHONE_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
)
from users.managers import UserManager
from users.service import get_font


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, blank=True, null=True, unique=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    skills = models.ManyToManyField('projects.Skill', blank=True, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def __str__(self):
        return f'{self.name} {self.surname}'

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self._generate_avatar()
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        color = random.choice(AVATAR_COLORS)
        letter = (self.name[0] if self.name else '?').upper()

        img = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), color)
        draw = ImageDraw.Draw(img)
        font = get_font(AVATAR_FONT_SIZE)

        bbox = draw.textbbox(AVATAR_TEXT_ANCHOR, letter, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        x = (AVATAR_SIZE - width) / 2 - bbox[0]
        y = (AVATAR_SIZE - height) / 2 - bbox[1]
        draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        filename = f'avatar_{self.email.split("@")[0]}.png'
        self.avatar.save(filename, ContentFile(buf.read()), save=False)
