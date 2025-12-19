# api/management/commands/seed_demo_content.py
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Book, Tool

BOOKS = [
    {
        "title": "Deep Learning with Python",
        "author_name": "François Chollet",
        "description": "Practical introduction to deep learning using Keras and TensorFlow.",
        "cover_url": "https://picsum.photos/id/1025/800/600",
        "buy_url": "https://www.manning.com/books/deep-learning-with-python",
        "is_featured": True,
        "keywords": ["Deep Learning", "Keras", "TensorFlow"],
    },
    {
        "title": "Clean Code",
        "author_name": "Robert C. Martin",
        "description": "A handbook of agile software craftsmanship.",
        "cover_url": "https://picsum.photos/id/1005/800/600",
        "buy_url": "https://www.pearson.com/en-us/subject-catalog/p/clean-code-a-handbook-of-agile-software-craftsmanship/P200000001093/9780132350884",
        "is_featured": True,
        "keywords": ["Software Engineering", "Best Practices"],
    },
    {
        "title": "Designing Data-Intensive Applications",
        "author_name": "Martin Kleppmann",
        "description": "The big ideas behind reliable, scalable, and maintainable systems.",
        "cover_url": "https://picsum.photos/id/1011/800/600",
        "buy_url": "https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/",
        "keywords": ["Databases", "Systems", "Scalability"],
    },
    {
        "title": "Python Crash Course",
        "author_name": "Eric Matthes",
        "description": "A fast-paced, thorough introduction to Python.",
        "cover_url": "https://picsum.photos/id/1035/800/600",
        "buy_url": "https://nostarch.com/pythoncrashcourse2e",
        "keywords": ["Python", "Beginner"],
    },
    {
        "title": "The Pragmatic Programmer",
        "author_name": "Andrew Hunt, David Thomas",
        "description": "Classic tips and practices for pragmatic software development.",
        "cover_url": "https://picsum.photos/id/1043/800/600",
        "buy_url": "https://www.pearson.com/en-us/subject-catalog/p/the-pragmatic-programmer-20th-anniversary-edition/P200000002326/9780135957059",
        "keywords": ["Pragmatism", "Craftsmanship"],
    },
]

TOOLS = [
    {
        "name": "Postman",
        "description": "Collaborative platform for API building and testing.",
        "image_url": "https://picsum.photos/id/1062/800/600",
        "link_url": "https://www.postman.com/",
        "is_featured": True,
        "keywords": ["API", "Testing"],
    },
    {
        "name": "Notion",
        "description": "All-in-one workspace for notes, docs, and collaboration.",
        "image_url": "https://picsum.photos/id/1069/800/600",
        "link_url": "https://www.notion.so/",
        "keywords": ["Docs", "Productivity"],
    },
    {
        "name": "GitHub",
        "description": "Code hosting platform for version control and collaboration.",
        "image_url": "https://picsum.photos/id/1074/800/600",
        "link_url": "https://github.com/",
        "keywords": ["Git", "Collaboration"],
    },
    {
        "name": "Figma",
        "description": "Design tool for teams who build products together.",
        "image_url": "https://picsum.photos/id/1084/800/600",
        "link_url": "https://www.figma.com/",
        "keywords": ["Design", "UI/UX"],
    },
    {
        "name": "AutoCount",
        "description": "Accounting & inventory management software.",
        "image_url": "https://picsum.photos/id/1081/800/600",
        "link_url": "https://www.autocountsoft.com/",
        "keywords": ["Accounting", "ERP"],
    },
]

class Command(BaseCommand):
    help = "Seed demo data (5 books + 5 tools). Safe to run multiple times."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing Books/Tools before seeding.")

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options.get("reset")
        if reset:
            self.stdout.write(self.style.WARNING("Deleting existing Book and Tool records..."))
            Book.objects.all().delete()
            Tool.objects.all().delete()

        # Books
        created_b, updated_b = 0, 0
        for b in BOOKS:
            obj, created = Book.objects.update_or_create(
                title=b["title"],
                defaults={
                    "author_name": b.get("author_name", ""),
                    "description": b.get("description", ""),
                    "cover_url": b.get("cover_url", ""),
                    "buy_url": b.get("buy_url", ""),
                    "is_featured": b.get("is_featured", False),
                    "is_published": True,
                    "request_enabled": True,
                    "keywords": b.get("keywords", []),
                },
            )
            created_b += 1 if created else 0
            updated_b += 0 if created else 1

        # Tools
        created_t, updated_t = 0, 0
        for t in TOOLS:
            obj, created = Tool.objects.update_or_create(
                name=t["name"],
                defaults={
                    "description": t.get("description", ""),
                    "image_url": t.get("image_url", ""),
                    "link_url": t.get("link_url", ""),
                    "is_featured": t.get("is_featured", False),
                    "is_published": True,
                    "request_enabled": True,
                    "keywords": t.get("keywords", []),
                },
            )
            created_t += 1 if created else 0
            updated_t += 0 if created else 1

        self.stdout.write(self.style.SUCCESS(
            f"Books -> created: {created_b}, updated: {updated_b} | "
            f"Tools -> created: {created_t}, updated: {updated_t}"
        ))
