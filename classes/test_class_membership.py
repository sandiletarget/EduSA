import pytest
from django.contrib.auth.models import User
from classes.models import Class, ClassMembership

@pytest.mark.django_db
def test_learner_can_join_class():
    # ARRANGE
    teacher = User.objects.create_user("teacher", password="123", is_staff=True)
    learner = User.objects.create_user("learner", password="123")

    classroom = Class.objects.create(
        name="Science",
        teacher=teacher,
        passcode="JOIN1234"
    )

    # ACT
    ClassMembership.objects.create(
        learner=learner,
        classroom=classroom
    )

    # ASSERT
    assert ClassMembership.objects.filter(
        learner=learner,
        classroom=classroom
    ).exists()
