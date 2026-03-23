from django.core.files.base import ContentFile
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages as django_messages

from dashboard.models import Station, WaterLevelReading
from .models import Report
from .pdf_generator import generate_station_report


def report_list(request):
    """List all generated reports."""
    reports = Report.objects.select_related("station").all()
    stations = Station.objects.filter(is_active=True)
    return render(
        request,
        "dashboard/report_list.html",
        {"reports": reports, "stations": stations},
    )


def report_generate(request):
    """Generate a new PDF report for a station."""
    if request.method != "POST":
        return redirect("reports:report_list")

    station_id = request.POST.get("station_id")
    days = int(request.POST.get("days", 7))
    station = get_object_or_404(Station, pk=station_id)

    date_to = timezone.now()
    date_from = date_to - timezone.timedelta(days=days)

    readings = list(
        WaterLevelReading.objects.filter(
            station=station, timestamp__gte=date_from
        ).order_by("timestamp")
    )

    # Get AI summary — falls back to statistical summary on any error
    from reports.summarizer import generate_summary, _generate_fallback_summary

    try:
        ai_summary = generate_summary(station, readings)
    except Exception:
        ai_summary = _generate_fallback_summary(station, readings)

    pdf_buffer = generate_station_report(
        station, readings, ai_summary, date_from, date_to
    )

    title = f"{station.name} - Water Level Report"
    report = Report.objects.create(
        station=station,
        title=title,
        ai_summary=ai_summary,
        date_from=date_from,
        date_to=date_to,
    )
    filename = f"hydrowatch_{station.station_id}_{date_to:%Y%m%d}.pdf"
    report.pdf_file.save(filename, ContentFile(pdf_buffer.read()), save=True)

    django_messages.success(request, f"Report generated: {title}")
    return redirect("reports:report_list")


def report_download(request, pk):
    """Download a generated PDF report."""
    report = get_object_or_404(Report, pk=pk)
    return FileResponse(
        report.pdf_file.open("rb"),
        as_attachment=True,
        filename=report.pdf_file.name.split("/")[-1],
    )
