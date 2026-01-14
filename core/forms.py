from django import forms

from classes.models import Class as Classroom
from .models import Lesson


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "content"]


class JoinClassForm(forms.Form):
    passcode = forms.CharField(
        label="Class passcode",
        max_length=8,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter 8-character passcode",
                "autocomplete": "off",
                "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
            }
        ),
    )

    error_messages = {
        "invalid_passcode": "We couldn't find a class with that passcode.",
    }

    def clean_passcode(self):
        code = self.cleaned_data["passcode"].upper()
        try:
            classroom = Classroom.objects.get(passcode=code)
        except Classroom.DoesNotExist:
            raise forms.ValidationError(
                self.error_messages["invalid_passcode"],
                code="invalid_passcode",
            )
        self.classroom = classroom
        return code