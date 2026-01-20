from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import engines
from django.utils.http import url_has_allowed_host_and_scheme

from classes.models import Class as Classroom, ClassMembership

from .accounts.decorators import student_required
from .forms import ExamForm, JoinClassForm
from .models import Exam, Lesson, Progress, QuizResult
from .utils import ROLE_DASHBOARD, dashboard_for_user, resolve_user_role


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
    if dashboard:
        return redirect(dashboard)
    return redirect("choose_role")



def login_view(request):
    if request.user.is_authenticated:
        return redirect("teacher_dashboard" if request.user.is_staff else "student_dashboard")

    next_url = request.POST.get("next") or request.GET.get("next")
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            dashboard_name = dashboard_for_user(user)
            if not dashboard_name:
                dashboard_name = "choose_role"
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
    redirect_response = _dispatch_dashboard_redirect(request, "teacher")
    if redirect_response:
        return redirect_response

    lessons = Lesson.objects.all()
    classes = Classroom.objects.filter(teacher=request.user)
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, "core/teacher_dashboard.html", {
        "lessons": lessons,
        "classes": classes,
        "exams": exams,
        "role_theme": "teacher",
    })


@login_required
@user_passes_test(is_teacher)
def lesson_create(request):
    if request.method == "POST":
        lesson = Lesson(title=request.POST.get("title", ""))
        lesson.description = request.POST.get("description", "")
        lesson.save()
        return redirect("teacher_dashboard")
    return render(request, "core/lesson_form.html")


@login_required
@user_passes_test(is_teacher)
def lesson_edit(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == "POST":
        lesson.title = request.POST.get("title", lesson.title)
        lesson.description = request.POST.get("description", lesson.description)
        lesson.save()
        return redirect("teacher_dashboard")
    return render(request, "core/lesson_form.html", {"lesson": lesson})


@login_required
@user_passes_test(is_teacher)
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
    redirect_response = _dispatch_dashboard_redirect(request, "student")
    if redirect_response:
        return redirect_response

    lessons = Lesson.objects.all()
    memberships = ClassMembership.objects.filter(learner=request.user).select_related("classroom")
    classrooms = [membership.classroom for membership in memberships]
    exams = Exam.objects.filter(classroom__in=classrooms)
    return render(request, "core/student_dashboard.html", {
        "lessons": lessons,
        "classrooms": classrooms,
        "exams": exams,
        "role_theme": "student",
    })


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
