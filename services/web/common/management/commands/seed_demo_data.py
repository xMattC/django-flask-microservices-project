import random
from datetime import timedelta
from pathlib import Path

from clients.projects_service_client import (
    create_project,
    delete_project,
    get_projects,
)
from clients.tasks_service_client import (
    create_task,
    delete_a_task,
    get_tasks,
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
    help = "Seed demo projects, tasks and time entries."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="demo@example.com")
        parser.add_argument("--password", default="demo12345")
        parser.add_argument("--projects", type=int, default=5)
        parser.add_argument("--min-entries", type=int, default=3)
        parser.add_argument("--max-entries", type=int, default=30)
        parser.add_argument("--days", type=int, default=365)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo data before reseeding.",
        )

    def handle(self, *args, **options):

        user = self.create_demo_user(
            email=options["email"],
            password=options["password"],
        )

        if options["reset"]:
            self.reset_demo_data(user.id)

        projects = self.seed_projects(
            user_id=user.id,
            project_count=options["projects"],
        )

        self.seed_tasks(
            user_id=user.id,
            projects=projects,
        )

        self.seed_time_entries(
            user_id=user.id,
            projects=projects,
            min_entries=options["min_entries"],
            max_entries=options["max_entries"],
            days=options["days"],
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    # ------------------------------------------------------------------
    # User
    # ------------------------------------------------------------------

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

        return user

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset_demo_data(self, user_id):

        self.stdout.write("Removing existing demo data...")

        #
        # Tasks
        #

        for task in get_tasks(user_id=user_id):
            delete_a_task(
                user_id=user_id,
                task_id=task["id"],
            )

        #
        # Time entries
        #

        for entry in get_time_entries(user_id=user_id):
            delete_time_entry(
                user_id=user_id,
                time_entry_id=entry["id"],
            )

        #
        # Projects
        #

        for project in get_projects(user_id=user_id):
            delete_project(
                user_id=user_id,
                project_id=project["id"],
            )

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def seed_projects(self, user_id, project_count):
        adjectives = [
            "Atlas",
            "Silver",
            "North",
            "Prime",
            "Summit",
            "Vertex",
            "Pioneer",
            "Evergreen",
            "Blue",
            "Nova",
        ]

        nouns = [
            "Analytics",
            "Platform",
            "Solutions",
            "Systems",
            "Operations",
            "Logistics",
            "Research",
            "Consulting",
            "Technologies",
            "Dynamics",
        ]

        adjective_pool = random.sample(adjectives, len(adjectives))
        noun_pool = random.sample(nouns, len(nouns))

        projects = []
        used = set()

        while len(projects) < project_count:

            if not adjective_pool:
                adjective_pool = random.sample(adjectives, len(adjectives))

            if not noun_pool:
                noun_pool = random.sample(nouns, len(nouns))

            name = f"{adjective_pool.pop()} {noun_pool.pop()}"

            if name in used:
                continue

            used.add(name)

            project = create_project(
                user_id=user_id,
                payload={
                    "name": name,
                    "description": f"Demo project for {name}.",
                },
            )

            projects.append(project)

        return projects

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------
    def seed_tasks(self, user_id, projects):

        task_directory = Path(__file__).parent / "demo_tasks"

        markdown_files = sorted(task_directory.glob("*.md"))

        if not markdown_files:
            self.stdout.write(self.style.WARNING("No demo task markdown files found."))
            return

        for project in projects:

            for markdown_file in markdown_files:

                markdown = markdown_file.read_text(encoding="utf-8").strip()

                #
                # First line becomes the title
                #

                title = markdown.splitlines()[0]

                if title.startswith("#"):
                    title = title.lstrip("#").strip()

                create_task(
                    user_id=user_id,
                    payload={
                        "project_id": project["id"],
                        "task_name": title,
                        "description": markdown,
                        "state": random.choice(
                            [
                                "to-do",
                                "in-progress",
                                "done",
                            ]
                        ),
                    },
                )

    # ------------------------------------------------------------------
    # Time Entries
    # ------------------------------------------------------------------
    def seed_time_entries(self, user_id, projects, min_entries, max_entries, days):

        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

        for project in projects:

            entry_count = random.randint(
                min_entries,
                max_entries,
            )

            for i in range(entry_count):

                description = f"Demo session {i + 1} " f"for {project['name']}"

                started_at = (
                    twenty_four_hours_ago - timedelta(days=random.randint(0, days))
                ).replace(
                    hour=random.randint(8, 16),
                    minute=random.choice([0, 15, 30, 45]),
                    second=0,
                    microsecond=0,
                )

                ended_at = started_at + timedelta(
                    minutes=random.choice([60, 75, 90, 105, 120, 150, 180, 240])
                )

                entry = create_time_entry(
                    user_id=user_id,
                    payload={
                        "project_id": project["id"],
                        "description": description,
                    },
                )

                stopped = stop_time_entry(
                    user_id=user_id,
                    time_entry_id=entry["id"],
                )

                update_time_entry(
                    user_id=user_id,
                    time_entry_id=stopped["id"],
                    payload={
                        "project_id": project["id"],
                        "description": description,
                        "started_at": started_at.isoformat(),
                        "ended_at": ended_at.isoformat(),
                    },
                )
