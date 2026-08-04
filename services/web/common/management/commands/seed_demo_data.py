import random
from datetime import timedelta

from clients.projects_service_client import (
    create_project,
    delete_project,
    get_projects,
)
from clients.time_tracking_service_client import (
    create_time_entry,
    delete_time_entry,
    get_time_entries,
    stop_time_entry,
    update_time_entry,
)
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Seed demo projects and time entries."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="demo@example.com")
        parser.add_argument("--password", default="demo12345")
        parser.add_argument("--projects", type=int, default=12)
        parser.add_argument("--min-entries", type=int, default=3)
        parser.add_argument("--max-entries", type=int, default=30)
        parser.add_argument("--days", type=int, default=365)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing demo user data before reseeding.",
        )

    def handle(self, *args, **options):
        user = self.create_demo_user(
            email=options["email"],
            password=options["password"],
        )

        if options["reset"]:
            self.reset_demo_data(user_id=user.id)

        projects = self.seed_projects(
            user_id=user.id,
            project_count=options["projects"],
        )

        self.seed_time_entries(
            user_id=user.id,
            projects=projects,
            min_entries=options["min_entries"],
            max_entries=options["max_entries"],
            days=options["days"],
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(f"Demo user: {options['email']}")
        self.stdout.write(f"Demo password: {options['password']}")

    def create_demo_user(self, email, password):
        User = get_user_model()

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": "Demo User",
                "is_active": True,
            },
        )

        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(f"Created demo user: {email}")
        else:
            self.stdout.write(f"Demo user already exists: {email}")

        return user

    def reset_demo_data(self, user_id):
        self.stdout.write("Resetting demo data...")

        existing_entries = get_time_entries(user_id=user_id)

        for entry in existing_entries:
            delete_time_entry(
                user_id=user_id,
                time_entry_id=entry["id"],
            )

        self.stdout.write(f"Deleted {len(existing_entries)} time entries.")

        existing_projects = get_projects(user_id=user_id)

        for project in existing_projects:
            delete_project(
                user_id=user_id,
                project_id=project["id"],
            )

        self.stdout.write(f"Deleted {len(existing_projects)} projects.")

    def seed_projects(self, user_id, project_count):
        adjectives = [
            "Global",
            "Dynamic",
            "NextGen",
            "Quantum",
            "Blue",
            "Silver",
            "Rapid",
            "Smart",
            "Bright",
            "Unified",
        ]

        nouns = [
            "Solutions",
            "Systems",
            "Technologies",
            "Concepts",
            "Networks",
            "Analytics",
            "Ventures",
            "Labs",
            "Industries",
            "Partners",
        ]

        existing_projects = get_projects(user_id=user_id)
        existing_names = {project["name"] for project in existing_projects}

        projects = list(existing_projects)
        generated_names = set(existing_names)

        while len(projects) < project_count:
            name = f"{random.choice(adjectives)} {random.choice(nouns)}"

            if name in generated_names:
                continue

            generated_names.add(name)

            project = create_project(
                user_id=user_id,
                payload={
                    "name": name,
                    "description": f"Demo project for {name}.",
                },
            )

            projects.append(project)
            self.stdout.write(f"Created project: {name}")

        return projects[:project_count]

    def seed_time_entries(self, user_id, projects, min_entries, max_entries, days):
        now = timezone.now()

        for project in projects:
            entry_count = random.randint(min_entries, max_entries)

            for index in range(entry_count):
                description = f"Demo work session {index + 1} for {project['name']}"

                days_back = random.randint(0, days)
                start_hour = random.randint(8, 15)
                start_minute = random.choice([0, 15, 30, 45])
                duration_hours = random.uniform(1, 4)

                started_at = (now - timedelta(days=days_back)).replace(
                    hour=start_hour,
                    minute=start_minute,
                    second=0,
                    microsecond=0,
                )

                ended_at = started_at + timedelta(hours=duration_hours)

                entry = create_time_entry(
                    user_id=user_id,
                    payload={
                        "project_id": project["id"],
                        "description": description,
                    },
                )

                stopped_entry = stop_time_entry(
                    user_id=user_id,
                    time_entry_id=entry["id"],
                )

                update_time_entry(
                    user_id=user_id,
                    time_entry_id=stopped_entry["id"],
                    payload={
                        "project_id": project["id"],
                        "description": description,
                        "started_at": started_at.isoformat(),
                        "ended_at": ended_at.isoformat(),
                    },
                )

                self.stdout.write(f"Created time entry: {description}")
