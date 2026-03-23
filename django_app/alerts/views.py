from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages as django_messages

from .forms import AlertRuleForm
from .models import AlertEvent, AlertRule


def alert_list(request):
    """List all alert rules and recent events."""
    rules = AlertRule.objects.select_related("station").all()
    recent_events = AlertEvent.objects.select_related("rule__station")[:20]
    return render(
        request,
        "alerts/alert_list.html",
        {"rules": rules, "recent_events": recent_events},
    )


def alert_create(request):
    """Create a new alert rule."""
    if request.method == "POST":
        form = AlertRuleForm(request.POST)
        if form.is_valid():
            form.save()
            django_messages.success(request, "Alert rule created successfully.")
            return redirect("alerts:alert_list")
    else:
        form = AlertRuleForm()
    return render(request, "alerts/alert_form.html", {"form": form})


def alert_delete(request, pk):
    """Delete an alert rule."""
    rule = get_object_or_404(AlertRule, pk=pk)
    if request.method == "POST":
        rule.delete()
        django_messages.success(request, "Alert rule deleted.")
        return redirect("alerts:alert_list")
    return render(request, "alerts/alert_confirm_delete.html", {"rule": rule})
