import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from classes.models import Class, ClassMembership

@pytest.mark.django_db
def test_join_class_view(client):
    # ARRANGE
    teacher = User.objects.create_user("teacher", password="123", is_staff=True)
    learner = User.objects.create_user("learner", password="123")

    classroom = Class.objects.create(
        name="English",
        teacher=teacher,
        passcode="PASS1234"
    )

    # ACT
    client.login(username="learner", password="123")

    response = client.post(
        reverse("classes:join_class"),
        {"passcode": "PASS1234"}
    )

    # ASSERT
    assert response.status_code == 302
    assert ClassMembership.objects.filter(
        learner=learner,
        classroom=classroom
    ).exists()
