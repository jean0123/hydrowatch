from django import forms

from .models import AlertRule


class AlertRuleForm(forms.ModelForm):
    class Meta:
        model = AlertRule
        fields = ["station", "metric", "operator", "threshold", "email"]
        widgets = {
            "station": forms.Select(attrs={"class": "form-select"}),
            "metric": forms.Select(attrs={"class": "form-select"}),
            "operator": forms.Select(attrs={"class": "form-select"}),
            "threshold": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
