from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import engines
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from classes.models import Class as Classroom, ClassMembership

from .accounts.decorators import student_required
from .forms import ExamForm, JoinClassForm, LessonForm
from .models import (
    Exam,
    ExamAnswer,
    ExamAttempt,
    ExamOption,
    ExamQuestion,
    Formula,
    Grade,
    Lesson,
    Course,
    CourseAnnouncement,
    CourseEnrollment,
    Resource,
    CourseProgress,
    CourseTermProgress,
    ActivityLog,
    LessonBookmark,
    LessonNote,
    Progress,
    QuizResult,
    StudentProgress,
    Subject,
)
from .utils import ROLE_DASHBOARD, dashboard_for_user, resolve_user_role, is_curriculum_admin, course_for_lesson


django_engine = engines["django"]
JOIN_CLASS_TEMPLATE = django_engine.from_string(
    """
    {% extends "core/base.html" %}
    {% block content %}
    <div class="max-w-2xl mx-auto rounded-2xl bg-white/90 p-8 shadow-xl">
        <h1 class="text-3xl font-semibold text-slate-900">Join a class</h1>
        {% if messages %}
            <div class="mt-4 space-y-2">
                {% for message in messages %}
                    <div class="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
        <form method="post" novalidate class="mt-6 space-y-4">
            {% csrf_token %}
            {% if form.non_field_errors %}
                <div class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                    {% for error in form.non_field_errors %}
                        {{ error }}
                    {% endfor %}
                </div>
            {% endif %}
            <div class="space-y-1 text-sm font-medium text-slate-700">
                {{ form.passcode.label_tag }}
                {{ form.passcode }}
            </div>
            {% if form.passcode.errors %}
                <p class="text-sm text-red-600">{{ form.passcode.errors|join:", " }}</p>
            {% endif %}
            <button type="submit" class="w-full rounded-lg bg-sky-600 px-4 py-2 text-white shadow-sm hover:bg-sky-500">
                Join class
            </button>
        </form>
    </div>
    {% endblock %}
    """
)


def _dispatch_dashboard_redirect(request, expected_role):
    normalized_role = resolve_user_role(request.user)
    if normalized_role == expected_role:
        return None
    dashboard = ROLE_DASHBOARD.get(normalized_role)
    return redirect(dashboard or "choose_role")



def login_view(request):
    if request.user.is_authenticated:
        return redirect("teacher_dashboard" if request.user.is_staff else "student_dashboard")

    next_url = request.POST.get("next") or request.GET.get("next")
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if (user := authenticate(request, username=username, password=password)):
            login(request, user)
            dashboard_name = dashboard_for_user(user) or "choose_role"
            allowed_hosts = {request.get_host()}
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=allowed_hosts, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect(dashboard_name)

        error = "Invalid username or password."

    return render(request, "core/login.html", {
        "error": error,
        "next": next_url,
    })


def logout_view(request):
    logout(request)
    return redirect("login")


def is_teacher(user):
    return user.is_staff


def is_admin(user):
    return is_curriculum_admin(user)


@login_required
def choose_role(request):
    current_role = resolve_user_role(request.user)
    if current_role in ROLE_DASHBOARD:
        return redirect(ROLE_DASHBOARD[current_role])

    if request.method == "POST":
        selected = (request.POST.get("role") or "").strip().lower()
        if selected in ROLE_DASHBOARD:
            students_group, _ = Group.objects.get_or_create(name="Students")
            teachers_group, _ = Group.objects.get_or_create(name="Teachers")

            if selected == "teacher":
                request.user.groups.add(teachers_group)
                request.user.groups.remove(students_group)
                request.user.is_staff = True
            else:
                request.user.groups.add(students_group)
                request.user.groups.remove(teachers_group)
                request.user.is_staff = False

            update_fields = ["is_staff"]
            if hasattr(request.user, "role"):
                request.user.role = selected
                update_fields.append("role")

            request.user.save(update_fields=update_fields)
            return redirect(ROLE_DASHBOARD[selected])

        messages.error(request, "Please choose a valid role.")

    return render(request, "core/choose_role.html")


@login_required
def teacher_dashboard(request):
    if redirect_response := _dispatch_dashboard_redirect(request, "teacher"):
        return redirect_response

    lessons = Lesson.published_for_active_caps()
    classes = Classroom.objects.filter(teacher=request.user)
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, "core/teacher_dashboard.html", {
        "lessons": lessons,
        "classes": classes,
        "exams": exams,
        "role_theme": "teacher",
    })


@login_required
@user_passes_test(is_admin)
def lesson_create(request):
    form = LessonForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Lesson created.")
        return redirect("teacher_dashboard")
    return render(request, "core/lesson_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def lesson_edit(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    form = LessonForm(request.POST or None, request.FILES or None, instance=lesson)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Lesson updated.")
        return redirect("teacher_dashboard")
    return render(request, "core/lesson_form.html", {"form": form, "lesson": lesson})


@login_required
@user_passes_test(is_admin)
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    lesson.delete()
    return redirect("teacher_dashboard")


@login_required
@user_passes_test(is_teacher)
def exam_create(request):
    form = ExamForm(request.POST or None, teacher=request.user)
    if request.method == "POST" and form.is_valid():
        exam = form.save(commit=False)
        exam.created_by = request.user
        exam.save()
        messages.success(request, "Exam created successfully.")
        return redirect("teacher_dashboard")
    return render(request, "teachers/exam_form.html", {"form": form})


@login_required
def student_dashboard(request):
    if redirect_response := _dispatch_dashboard_redirect(request, "student"):
        return redirect_response

    lessons = Lesson.published_for_active_caps()
    memberships = ClassMembership.objects.filter(learner=request.user).select_related("classroom")
    classrooms = [membership.classroom for membership in memberships]
    exams = Exam.objects.filter(classroom__in=classrooms)
    learner_grade = getattr(request.user, "grade", None)
    if learner_grade is None and hasattr(request.user, "profile"):
        learner_grade = getattr(request.user.profile, "grade", None)
    if not learner_grade:
        learner_grade = 10
    grades = list(range(4, 13))
    return render(request, "core/student_dashboard.html", {
        "lessons": lessons,
        "classrooms": classrooms,
        "exams": exams,
        "role_theme": "student",
        "learner_grade": learner_grade,
        "grades": grades,
    })


@login_required
def lesson_catalog(request):
    grade_number = request.GET.get("grade")
    subject_slug = request.GET.get("subject")

    grade = Grade.objects.filter(number=grade_number).first() if grade_number else Grade.objects.first()
    subjects = Subject.objects.all()

    lessons = Lesson.published_for_active_caps().select_related("grade_ref", "subject_ref", "topic_ref", "subtopic_ref")
    if grade:
        lessons = lessons.filter(models.Q(grade_ref=grade) | models.Q(grade=str(grade.number)))
    if subject_slug:
        lessons = lessons.filter(models.Q(subject_ref__slug=subject_slug) | models.Q(subject__iexact=subject_slug.replace("-", " ")))

    paginator = Paginator(lessons, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    progress_map = {
        progress.lesson_id: progress
        for progress in StudentProgress.objects.filter(student=request.user, lesson__in=page_obj)
    }

    bookmarks = {
        bookmark.lesson_id
        for bookmark in LessonBookmark.objects.filter(student=request.user, lesson__in=page_obj)
    }

    lesson_cards = [
        {
            "lesson": lesson,
            "progress": progress_map.get(lesson.id),
            "bookmarked": lesson.id in bookmarks,
        }
        for lesson in page_obj
    ]

    return render(request, "core/lessons/lesson_catalog.html", {
        "grade": grade,
        "subjects": subjects,
        "lesson_cards": lesson_cards,
        "page_obj": page_obj,
    })


@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, is_published=True, caps_version__is_active=True)
    progress, _ = StudentProgress.objects.get_or_create(student=request.user, lesson=lesson)
    progress.last_opened_at = timezone.now()
    progress.save(update_fields=["last_opened_at"])

    course = course_for_lesson(lesson)
    ActivityLog.objects.create(user=request.user, course=course, lesson=lesson, action="lesson_view")

    bookmarked = LessonBookmark.objects.filter(student=request.user, lesson=lesson).exists()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "complete":
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save(update_fields=["completed", "completed_at"])
            ActivityLog.objects.create(user=request.user, course=course, lesson=lesson, action="lesson_complete")
            if course:
                completed = StudentProgress.objects.filter(student=request.user, lesson__in=Lesson.objects.filter(grade_ref=course.grade, subject_ref=course.subject, caps_version=course.caps_version), completed=True).count()
                total = Lesson.objects.filter(grade_ref=course.grade, subject_ref=course.subject, caps_version=course.caps_version, is_published=True).count() or 1
                percent = round((completed / total) * 100, 2)
                CourseProgress.objects.update_or_create(
                    user=request.user,
                    course=course,
                    defaults={"percent_complete": percent},
                )
                CourseTermProgress.objects.update_or_create(
                    user=request.user,
                    course=course,
                    term=lesson.term,
                    defaults={"completed": True},
                )
            messages.success(request, "Lesson marked as completed.")
            return redirect("lesson_detail", pk=lesson.pk)
        if action == "bookmark":
            LessonBookmark.objects.get_or_create(student=request.user, lesson=lesson)
            messages.success(request, "Lesson bookmarked.")
            return redirect("lesson_detail", pk=lesson.pk)
        if action == "unbookmark":
            LessonBookmark.objects.filter(student=request.user, lesson=lesson).delete()
            messages.info(request, "Bookmark removed.")
            return redirect("lesson_detail", pk=lesson.pk)
        if action == "note":
            if (content := (request.POST.get("note") or "").strip()):
                LessonNote.objects.create(student=request.user, lesson=lesson, content=content)
                messages.success(request, "Note saved.")
            return redirect("lesson_detail", pk=lesson.pk)
    return render(request, "core/lessons/lesson_detail.html", {
        "lesson": lesson,
        "progress": progress,
        "bookmarked": bookmarked,
        "notes": LessonNote.objects.filter(student=request.user, lesson=lesson),
        "grades": list(range(4, 13)),
    })


@login_required
def lesson_detail_slug(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug, is_published=True, caps_version__is_active=True)
    return lesson_detail(request, lesson.pk)


@login_required
def course_list_api(request):
    grade_number = request.GET.get("grade")
    subject_slug = request.GET.get("subject")
    caps = Course.objects.filter(caps_version__is_active=True, is_published=True)
    if grade_number:
        caps = caps.filter(grade__number=grade_number)
    if subject_slug:
        caps = caps.filter(subject__slug=subject_slug)
    payload = [
        {
            "id": course.id,
            "caps_year": course.caps_version.year,
            "grade": course.grade.number,
            "subject": course.subject.slug,
            "title": course.title or str(course),
        }
        for course in caps
    ]
    return JsonResponse({"courses": payload})


@login_required
def course_detail_api(request, course_id):
    course = get_object_or_404(Course, pk=course_id, caps_version__is_active=True, is_published=True)
    lessons = Lesson.published_for_active_caps().filter(
        grade_ref=course.grade,
        subject_ref=course.subject,
        caps_version=course.caps_version,
    ).order_by("term", "title")
    resources = Resource.objects.filter(
        caps_version=course.caps_version,
        grade=course.grade,
        subject=course.subject,
        is_published=True,
    ).order_by("-created_at")
    announcements = CourseAnnouncement.objects.filter(course=course, is_published=True)[:20]

    payload = {
        "course": {
            "id": course.id,
            "caps_year": course.caps_version.year,
            "grade": course.grade.number,
            "subject": course.subject.slug,
            "title": course.title or str(course),
        },
        "lessons": [
            {
                "id": lesson.id,
                "title": lesson.title,
                "term": lesson.term,
                "topic": lesson.topic,
                "slug": lesson.slug,
            }
            for lesson in lessons
        ],
        "resources": [
            {
                "id": resource.id,
                "title": resource.title,
                "type": resource.resource_type,
                "url": resource.url,
                "file": resource.file.url if resource.file else "",
            }
            for resource in resources
        ],
        "announcements": [
            {
                "id": announcement.id,
                "title": announcement.title,
                "message": announcement.message,
                "created_at": announcement.created_at.isoformat(),
            }
            for announcement in announcements
        ],
    }
    return JsonResponse(payload)


@login_required
def notifications_api(request):
    notifications = request.user.notifications.all()[:50]
    return JsonResponse({
        "notifications": [
            {
                "id": note.id,
                "title": note.title,
                "message": note.message,
                "link": note.link,
                "created_at": note.created_at.isoformat(),
                "read_at": note.read_at.isoformat() if note.read_at else None,
            }
            for note in notifications
        ]
    })


@login_required
def exam_list(request):
    exams = Exam.objects.filter(is_published=True).select_related("grade_ref", "subject_ref")
    return render(request, "core/exams/exam_list.html", {"exams": exams})


@login_required
def exam_take(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id, is_published=True)
    questions = exam.questions.prefetch_related("options")

    if request.method == "POST":
        attempt = ExamAttempt.objects.create(exam=exam, student=request.user)
        total_score = 0

        for question in questions:
            answer_value = request.POST.get(f"question_{question.id}", "").strip()
            selected_option = None
            is_correct = False
            score_awarded = 0

            if question.question_type in {"mcq", "true_false"}:
                if answer_value.isdigit():
                    selected_option = ExamOption.objects.filter(pk=int(answer_value), question=question).first()
                is_correct = bool(selected_option and selected_option.is_correct)
            else:
                is_correct = answer_value.lower() == (question.correct_answer or "").strip().lower()

            if is_correct:
                score_awarded = question.points
                total_score += score_awarded

            ExamAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
                answer_text=answer_value,
                is_correct=is_correct,
                score_awarded=score_awarded,
            )

        attempt.score = total_score
        attempt.completed_at = timezone.now()
        attempt.save(update_fields=["score", "completed_at"])
        return redirect("exam_result", attempt_id=attempt.id)

    return render(request, "core/exams/exam_take.html", {
        "exam": exam,
        "questions": questions,
    })


@login_required
def exam_result(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, pk=attempt_id, student=request.user)
    answers = attempt.answers.select_related("question", "selected_option")
    return render(request, "core/exams/exam_result.html", {
        "attempt": attempt,
        "answers": answers,
    })


@login_required
def formulas_api(request):
    grade = request.GET.get("grade")
    subject = request.GET.get("subject")

    formulas = Formula.objects.all()
    if grade:
        try:
            formulas = formulas.filter(grade=int(grade))
        except (TypeError, ValueError):
            return JsonResponse({"error": "Invalid grade."}, status=400)
    if subject:
        formulas = formulas.filter(subject=subject)

    payload = [
        {
            "id": formula.id,
            "grade": formula.grade,
            "subject": formula.subject,
            "subject_label": formula.get_subject_display(),
            "topic": formula.topic,
            "formula_text": formula.formula_text,
            "explanation": formula.explanation,
        }
        for formula in formulas
    ]

    return JsonResponse({"formulas": payload})


@login_required
def lessons_api(request):
    grade = request.GET.get("grade")
    subject = request.GET.get("subject")

    lessons = Lesson.published_for_active_caps()
    if grade:
        lessons = lessons.filter(models.Q(grade_ref__number=grade) | models.Q(grade=grade))
    if subject:
        lessons = lessons.filter(models.Q(subject_ref__slug=subject) | models.Q(subject__iexact=subject.replace("-", " ")))

    payload = [
        {
            "id": lesson.id,
            "slug": lesson.slug,
            "title": lesson.title,
            "grade": lesson.grade_ref.number if lesson.grade_ref else lesson.grade,
            "subject": lesson.subject_ref.slug if lesson.subject_ref else lesson.subject,
            "topic": lesson.topic_ref.name if lesson.topic_ref else "",
        }
        for lesson in lessons
    ]
    return JsonResponse({"lessons": payload})


@login_required
def exams_api(request):
    grade = request.GET.get("grade")
    subject = request.GET.get("subject")

    exams = Exam.objects.filter(is_published=True)
    if grade:
        exams = exams.filter(models.Q(grade_ref__number=grade))
    if subject:
        exams = exams.filter(models.Q(subject_ref__slug=subject))

    payload = [
        {
            "id": exam.id,
            "title": exam.title,
            "grade": exam.grade_ref.number if exam.grade_ref else None,
            "subject": exam.subject_ref.slug if exam.subject_ref else None,
            "duration_minutes": exam.duration_minutes,
        }
        for exam in exams
    ]
    return JsonResponse({"exams": payload})


@login_required
@student_required
def student_progress(request):
    progress = Progress.objects.filter(student=request.user, completed=True).select_related("lesson")
    return render(request, "core/student_progress.html", {
        "progress": progress,
        "role_theme": "student",
    })


@login_required
@student_required
def join_class(request):
    form = JoinClassForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        classroom = form.classroom
        membership, created = ClassMembership.objects.get_or_create(
            classroom=classroom,
            learner=request.user,
        )
        if created:
            messages.success(request, f"You've joined {classroom.name}.")
        else:
            messages.info(request, f"You're already enrolled in {classroom.name}.")
        return redirect("classes:class_detail", pk=classroom.pk)

    return HttpResponse(
        JOIN_CLASS_TEMPLATE.render(
            {"form": form},
            request=request,
        )
    )


@staff_member_required
def teacher_quiz_results(request):
    results = QuizResult.objects.select_related("student", "quiz").order_by("-completed_at")
    return render(request, "teachers/quiz_results.html", {"results": results})


def verify_certificate(request):
    code = request.GET.get("code")
    result = None
    valid = False

    if code:
        try:
            result = QuizResult.objects.get(certificate_code=code)
            valid = True
        except QuizResult.DoesNotExist:
            result = None

    return render(request, "students/verify_certificate.html", {
        "code": code,
        "result": result,
        "valid": valid
    })
