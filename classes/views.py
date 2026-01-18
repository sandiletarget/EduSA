from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.forms import JoinClassForm
from .forms import ClassForm
from .models import Class, ClassMembership, LiveSession


@login_required
def class_detail(request, pk):
    classroom = get_object_or_404(Class, pk=pk)
    is_teacher = request.user == classroom.teacher
    memberships = classroom.memberships.select_related("learner").order_by("joined_at")
    membership = memberships.filter(learner=request.user).first()

    if not (is_teacher or membership):
        raise PermissionDenied

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
    return redirect("classes:class_detail", pk=classroom.pk)


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
    return redirect("classes:class_detail", pk=classroom.pk)


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
    if not request.user.is_staff:
        raise PermissionDenied

    form = ClassForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        classroom = form.save(commit=False)
        classroom.teacher = request.user
        classroom.save()
        messages.success(request, f"Class created. Passcode: {classroom.passcode}")
        return redirect("classes:class_detail", pk=classroom.pk)

    return render(request, "classes/class_form.html", {"form": form})
