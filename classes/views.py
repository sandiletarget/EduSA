import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.forms import JoinClassForm
from core.utils import resolve_user_role
from .forms import ClassForm
from .models import Class, ClassMembership, LiveSession


logger = logging.getLogger(__name__)


@login_required
def class_detail(request, pk):
    classroom = get_object_or_404(Class, pk=pk)
    is_teacher = request.user == classroom.teacher
    memberships = classroom.memberships.select_related("learner").order_by("joined_at")
    membership = memberships.filter(learner=request.user).first()

    if not (is_teacher or membership):
        messages.info(request, "Join the class to view details.")
        return redirect("classes:join_class")

    context = {
        "classroom": classroom,
        "is_teacher": is_teacher,
        "memberships": memberships,
        "active_session": classroom.live_sessions.filter(is_active=True).order_by("-started_at").first(),
    }
    return render(request, "classes/class_detail.html", context)


@login_required
def start_live_session(request, pk):
    classroom = get_object_or_404(Class, pk=pk)
    if request.user != classroom.teacher:
        raise PermissionDenied

    session, created = LiveSession.objects.get_or_create(classroom=classroom)
    session.is_active = True
    session.started_at = timezone.now()
    session.save(update_fields=["is_active", "started_at"])

    messages.success(request, "Live session started.")
    return redirect("classes:live_class_room", pk=classroom.pk)


@login_required
def join_live_session(request, pk):
    classroom = get_object_or_404(Class, pk=pk)
    membership = ClassMembership.objects.filter(classroom=classroom, learner=request.user).first()
    if not membership:
        raise PermissionDenied

    active_session = classroom.live_sessions.filter(is_active=True).order_by("-started_at").first()
    if not active_session:
        messages.warning(request, "There is no active live session to join right now.")
        return redirect("classes:class_detail", pk=classroom.pk)

    messages.success(request, "You joined the live session.")
    return redirect("classes:live_class_room", pk=classroom.pk)


@login_required
def live_class_room(request, pk):
    classroom = get_object_or_404(Class, pk=pk)
    is_teacher = request.user == classroom.teacher
    membership = ClassMembership.objects.filter(classroom=classroom, learner=request.user).first()

    if not (is_teacher or membership):
        raise PermissionDenied

    participants = classroom.memberships.select_related("learner").order_by("joined_at")
    active_session = classroom.live_sessions.filter(is_active=True).order_by("-started_at").first()

    template_name = "classes/live/live_class_teacher.html" if is_teacher else "classes/live/live_class_student.html"
    return render(request, template_name, {
        "classroom": classroom,
        "is_teacher": is_teacher,
        "participants": participants,
        "active_session": active_session,
        "session_duration": "00:12:45",
    })


@login_required
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

    return render(request, "classes/join_class.html", {"form": form})


@login_required
def create_class(request):
    if resolve_user_role(request.user) != "teacher":
        raise PermissionDenied

    form = ClassForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        classroom = form.save(commit=False)
        classroom.teacher = request.user
        try:
            classroom.save()
        except ValidationError as exc:
            form.add_error(None, exc)
        except DatabaseError:
            form.add_error(None, "Database error while creating the class. Please try again or contact support.")
        except Exception as exc:
            logger.exception("Unexpected error creating class", exc_info=exc)
            form.add_error(None, "Unexpected error while creating the class. Please try again.")
        else:
            messages.success(request, f"Class created. Passcode: {classroom.passcode}")
            return redirect("classes:class_detail", pk=classroom.pk)

    return render(request, "classes/class_form.html", {"form": form})
