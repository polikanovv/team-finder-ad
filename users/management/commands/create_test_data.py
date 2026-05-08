from django.core.management.base import BaseCommand

from projects.models import Project, Skill
from users.models import User


class Command(BaseCommand):
    help = 'Create test users and projects for review'

    def handle(self, *args, **options):
        if User.objects.filter(email='alice@example.com').exists():
            self.stdout.write('Test data already exists, skipping.')
            return

        skills_data = ['Python', 'Django', 'JavaScript', 'React', 'PostgreSQL', 'Docker']
        skills = {name: Skill.objects.get_or_create(name=name)[0] for name in skills_data}

        alice = User.objects.create_user(
            email='alice@example.com',
            name='Alice',
            surname='Smith',
            password='testpass123',
            about='Backend developer, loves Python and Django.',
            github_url='https://github.com/alice',
        )
        alice.skills.add(skills['Python'], skills['Django'], skills['PostgreSQL'])

        bob = User.objects.create_user(
            email='bob@example.com',
            name='Bob',
            surname='Johnson',
            password='testpass123',
            about='Frontend developer, React enthusiast.',
            github_url='https://github.com/bob',
        )
        bob.skills.add(skills['JavaScript'], skills['React'])

        carol = User.objects.create_user(
            email='carol@example.com',
            name='Carol',
            surname='Williams',
            password='testpass123',
            about='DevOps engineer, Docker and cloud infra.',
            github_url='https://github.com/carol',
        )
        carol.skills.add(skills['Docker'], skills['PostgreSQL'])

        p1 = Project.objects.create(
            name='Team Finder',
            description='A platform for finding project teammates by skills.',
            owner=alice,
            github_url='https://github.com/alice/team-finder',
            status='open',
        )
        p1.participants.add(alice, bob)
        p1.skills.add(skills['Python'], skills['Django'], skills['PostgreSQL'])

        p2 = Project.objects.create(
            name='React Dashboard',
            description='A modern analytics dashboard built with React.',
            owner=bob,
            github_url='https://github.com/bob/react-dashboard',
            status='open',
        )
        p2.participants.add(bob)
        p2.skills.add(skills['JavaScript'], skills['React'])

        p3 = Project.objects.create(
            name='DevOps Toolkit',
            description='A collection of Docker-based tools for CI/CD pipelines.',
            owner=carol,
            status='open',
        )
        p3.participants.add(carol, alice)
        p3.skills.add(skills['Docker'], skills['PostgreSQL'])

        p4 = Project.objects.create(
            name='Open Source Blog',
            description='A simple blog engine built with Django and PostgreSQL.',
            owner=alice,
            status='closed',
        )
        p4.participants.add(alice, carol)
        p4.skills.add(skills['Python'], skills['Django'])

        self.stdout.write(self.style.SUCCESS(
            'Created 3 users (alice, bob, carol) and 4 projects. Password for all: testpass123'
        ))
