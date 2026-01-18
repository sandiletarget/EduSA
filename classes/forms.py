from django import forms

from .models import Class


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
