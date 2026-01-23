from pathlib import Path
import re

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone

from core.models import CAPSVersion, Grade, Subject, Lesson


LESSON_HEADER = re.compile(r"^### Lesson\s+\d+", re.IGNORECASE)
FIELD_LINE = re.compile(r"^-\s*(?P<key>[^:]+):\s*(?P<value>.*)$")


class Command(BaseCommand):
    help = "Import curriculum markdown files into Lesson records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="curriculum",
            help="Path to curriculum markdown directory",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Mark imported lessons as published",
        )

    def handle(self, *args, **options):
        base_path = Path(options["path"]).resolve()
        publish = options["publish"]

        if not base_path.exists():
            self.stdout.write(self.style.ERROR(f"Path not found: {base_path}"))
            return

        caps = CAPSVersion.get_active()
        if not caps:
            year = timezone.now().year
            caps = CAPSVersion.objects.create(year=year, description=f"CAPS {year}", is_active=True)

        files = sorted(base_path.glob("grade-*.md"))
        if not files:
            self.stdout.write(self.style.ERROR("No grade-*.md files found."))
            return

        created_count = 0
        updated_count = 0

        for file in files:
            content = file.read_text(encoding="utf-8")
            sections = self._split_lessons(content)
            for lesson_block in sections:
                data = self._parse_lesson_block(lesson_block)
                if not data:
                    continue

                grade_number = int(data.get("Grade", 0) or 0)
                subject_name = data.get("Subject", "").strip()
                title = data.get("Lesson Title", "").strip()
                if not (grade_number and subject_name and title):
                    continue

                grade = self._get_or_create_grade(grade_number)
                subject = self._get_or_create_subject(subject_name)

                lesson, created = Lesson.objects.get_or_create(
                    caps_version=caps,
                    grade_ref=grade,
                    subject_ref=subject,
                    title=title,
                    defaults={
                        "term": int(data.get("Term", 1) or 1),
                        "topic": data.get("Topic", "").strip(),
                        "content": data.get("Lesson Content", "").strip(),
                        "key_concepts": data.get("Key Concepts", "").strip(),
                        "examples": data.get("Worked Example", "").strip(),
                        "summary": data.get("Summary", "").strip(),
                        "grade": f"Grade {grade_number}",
                        "subject": subject_name,
                        "is_published": publish,
                        "slug": None,
                    },
                )

                if not created:
                    lesson.term = int(data.get("Term", lesson.term) or lesson.term)
                    lesson.topic = data.get("Topic", lesson.topic)
                    lesson.content = data.get("Lesson Content", lesson.content)
                    lesson.key_concepts = data.get("Key Concepts", lesson.key_concepts)
                    lesson.examples = data.get("Worked Example", lesson.examples)
                    lesson.summary = data.get("Summary", lesson.summary)
                    if publish:
                        lesson.is_published = True
                    lesson.grade = f"Grade {grade_number}"
                    lesson.subject = subject_name
                    lesson.save()
                    updated_count += 1
                else:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import complete. Created: {created_count}, Updated: {updated_count}"
        ))

    def _split_lessons(self, text):
        lines = text.splitlines()
        blocks = []
        current = []
        in_block = False
        for line in lines:
            if LESSON_HEADER.match(line.strip()):
                if current:
                    blocks.append("\n".join(current))
                current = [line]
                in_block = True
                continue
            if in_block:
                current.append(line)
        if current:
            blocks.append("\n".join(current))
        return blocks

    def _parse_lesson_block(self, block):
        data = {}
        lines = block.splitlines()
        current_key = None
        buffer = []

        def flush():
            nonlocal buffer, current_key
            if current_key:
                data[current_key] = "\n".join(buffer).strip()
            buffer = []

        for line in lines:
            match = FIELD_LINE.match(line.strip())
            if match:
                flush()
                current_key = match.group("key").strip()
                value = match.group("value").strip()
                buffer.append(value)
            else:
                if current_key:
                    buffer.append(line.strip())
        flush()

        # Normalize lists
        if "Key Concepts" in data:
            concepts = []
            for line in data["Key Concepts"].splitlines():
                cleaned = line.replace("-", "").strip()
                if cleaned:
                    concepts.append(cleaned)
            data["Key Concepts"] = "\n".join(concepts)

        return data

    def _get_or_create_grade(self, number):
        phase = Grade.PHASE_INTERMEDIATE
        if 7 <= number <= 9:
            phase = Grade.PHASE_SENIOR
        elif number >= 10:
            phase = Grade.PHASE_FET
        grade, _ = Grade.objects.get_or_create(
            number=number,
            defaults={"label": f"Grade {number}", "phase": phase},
        )
        return grade

    def _get_or_create_subject(self, name):
        slug = slugify(name)
        subject, _ = Subject.objects.get_or_create(
            slug=slug,
            defaults={"name": name},
        )
        return subject
