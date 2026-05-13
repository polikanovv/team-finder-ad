from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from team_finder.constants import GITHUB_DOMAIN


class GitHubUrlMixin:
    def clean_github_url(self):
        url = (self.cleaned_data.get('github_url') or '').strip()
        if not url:
            return url
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError('Введите корректную ссылку')
        if GITHUB_DOMAIN not in url:
            raise ValidationError(f'Ссылка должна вести на GitHub ({GITHUB_DOMAIN})')
        return url
