import pytest
from django.contrib.auth.models import User
from classes.models import Class

@pytest.mark.django_db
def test_teacher_can_create_class():
    # ARRANGE (set up data)
    teacher = User.objects.create_user(
        username="teacher1",
        password="pass123",
        is_staff=True,
    )

    # ACT (do the thing)
    classroom = Class.objects.create(
        name="Math Grade 10",
        teacher=teacher,
        passcode="ABC12345"
    )

    # ASSERT (check result)
    assert classroom.teacher == teacher
    assert classroom.name == "Math Grade 10"
    assert classroom.passcode == "ABC12345"
