from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .enums import Priority
from .models import ChecklistItem, Task


class TaskForm(forms.ModelForm):
    justification = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = Task
        fields = [
            "name", "description", "project", "status", "priority",
            "task_kind", "scrum_points", "target_datetime", "tags", "assignees",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", "Enregistrer"))
        # Champ dépendant : les assignés se limitent aux membres du projet.
        if "project" in self.data:
            try:
                self.fields["assignees"].queryset = User.objects.filter(
                    member_projects__id=int(self.data.get("project"))
                )
            except (TypeError, ValueError):
                self.fields["assignees"].queryset = User.objects.none()
        elif self.instance.pk and self.instance.project_id:
            self.fields["assignees"].queryset = self.instance.project.members.all()
        else:
            self.fields["assignees"].queryset = User.objects.none()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("priority") == Priority.CRITICAL and not cleaned.get("justification"):
            self.add_error("justification", "Obligatoire pour une priorité Critique.")
        return cleaned


ChecklistFormSet = inlineformset_factory(
    Task, ChecklistItem, fields=["label", "done", "order"], extra=1, can_delete=True
)
