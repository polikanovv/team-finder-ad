import io
import os
import random

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, surname, password, **extra_fields)


def _get_font(size=50):
    paths = [
        'C:\\Windows\\Fonts\\arial.ttf',
        'C:\\Windows\\Fonts\\calibri.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = models.CharField(max_length=12, blank=True, null=True, unique=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    skills = models.ManyToManyField('projects.Skill', blank=True, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self._generate_avatar()
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        colors = [
            '#5B8DD9', '#7B68EE', '#E86A6A', '#4ECDC4',
            '#45B7D1', '#6BAF92', '#C87941', '#9A6EAF',
        ]
        color = random.choice(colors)
        letter = (self.name[0] if self.name else '?').upper()

        img = Image.new('RGB', (100, 100), color)
        draw = ImageDraw.Draw(img)
        font = _get_font(50)

        bbox = draw.textbbox((0, 0), letter, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (100 - w) / 2 - bbox[0]
        y = (100 - h) / 2 - bbox[1]
        draw.text((x, y), letter, fill='white', font=font)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        filename = f'avatar_{self.email.split("@")[0]}.png'
        self.avatar.save(filename, ContentFile(buf.read()), save=False)
