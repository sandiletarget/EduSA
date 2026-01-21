from django import forms

from .models import Assessment, Class, AssessmentSubmission


class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "placeholder": "Class name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "placeholder": "Class description",
                    "rows": 4,
                }
            ),
        }


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ["title", "instructions", "grade_ref", "subject_ref", "due_date", "allowed_file_types"]
        widgets = {
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
                    "placeholder": "Assessment title",
                }
            ),
            "instructions": forms.Textarea(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                    "rows": 4,
                }
            ),
            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
            "allowed_file_types": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            ),
        }


class AssessmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssessmentSubmission
        fields = ["submission_file"]
        widgets = {
            "submission_file": forms.ClearableFileInput(
                attrs={
                    "class": "mt-1 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-900",
                }
            )
        }

    def __init__(self, *args, allowed_extensions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_extensions = allowed_extensions or []

    def clean_submission_file(self):
        file = self.cleaned_data.get("submission_file")
        if file and self.allowed_extensions:
            ext = file.name.split(".")[-1].lower()
            if ext not in self.allowed_extensions:
                raise forms.ValidationError("File type not allowed.")
        return file
