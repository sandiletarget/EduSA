from django.contrib.auth.decorators import user_passes_test


def student_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and u.groups.filter(name='Students').exists()
    )(view_func)
