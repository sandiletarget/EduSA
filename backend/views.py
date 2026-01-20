from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from classes.models import Class, ClassMembership
from .models import LiveClassSession


@login_required
def live_class_room(request, class_id):
    classroom = get_object_or_404(Class, pk=class_id)
    is_teacher = request.user == classroom.teacher
    membership = ClassMembership.objects.filter(classroom=classroom, learner=request.user).first()

    if not (is_teacher or membership):
        raise PermissionDenied

    session, _ = LiveClassSession.objects.get_or_create(
        classroom=classroom,
        teacher=classroom.teacher,
        defaults={"status": LiveClassSession.STATUS_LIVE, "started_at": timezone.now()},
    )

    return render(request, "live/live_class_teacher.html" if is_teacher else "live/live_class_student.html", {
        "classroom": classroom,
        "session": session,
        "is_teacher": is_teacher,
    })
