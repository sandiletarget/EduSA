from django import forms

from classes.models import Class as Classroom
from .models import Exam, Lesson


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "content",
            "grade_ref",
            "subject_ref",
            "topic_ref",
            "subtopic_ref",
            "notes_text",
            "notes_file",
            "video_url",
            "formula_sheet",
            "cover_image",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "placeholder": "Lesson title",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "rows": 6,
                }
            ),
            "grade_ref": forms.Select(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
            "subject_ref": forms.Select(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
            "topic_ref": forms.Select(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
            "subtopic_ref": forms.Select(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
            "notes_text": forms.Textarea(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "rows": 4,
                }
            ),
            "video_url": forms.URLInput(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "placeholder": "https://...",
                }
            ),
        }


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


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["classroom", "grade_ref", "subject_ref", "title", "description", "due_date", "duration_minutes", "is_published"]
        widgets = {
            "classroom": forms.Select(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
            "grade_ref": forms.Select(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
            "subject_ref": forms.Select(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "placeholder": "Exam title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "placeholder": "Exam description",
                    "rows": 4,
                }
            ),
            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
            "duration_minutes": forms.NumberInput(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "min": 1,
                }
            ),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher is not None:
            self.fields["classroom"].queryset = Classroom.objects.filter(teacher=teacher)