# Standard library imports
from collections import Counter

# Django imports
from django.shortcuts import render, redirect
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, UpdateView, CreateView
from django.contrib import messages

# Local application imports
from reportgen.forms import (
    UniqueFindingForm,
    FindingForm,
    FindingScreenshotForm,
    ReportForm,
    ClientContactForm,
    RTContactForm,
    ScoreOverrideForm,
    StrengthForm,
    ImprovementForm,
    SolutionOverrideForm,
    GenerateReportForm,
)
from reportgen.models import (
    Report,
    Finding,
    FindingScreenshot,
    ClientContact,
    RTContact,
    ScoreOverride,
    Strength,
    Improvement,
    SolutionOverride,
)
from reportgen.admin import generate_report_type


# Create your views here.
def unique_findings(request):
    form = UniqueFindingForm()
    results = []
    if request.method == "POST":
        form_data = UniqueFindingForm(request.POST)
        if form_data.is_valid():
            engagement_name = form_data.cleaned_data["engagement_name"]
            report_objs = Report.objects.filter(report_for__istartswith=engagement_name)
            if report_objs:
                report_obj = report_objs.first()
                engagement_groups = report_obj.findings.all()
                if engagement_groups:
                    for eng_group in engagement_groups:
                        findings = eng_group.findings.all().filter(CVSS_v2_0_Base_Score__gt=0).values_list('Name', flat=True)
                        if findings:
                            results.extend(findings)
    if results:
        results = dict(Counter(results).most_common())
    else:
        results = {}
    return render(request, "unique_findings.html", {'formset': form, 'results': results})

def list_services(request):
    form = UniqueFindingForm()
    results = []
    if request.method == "POST":
        form_data = UniqueFindingForm(request.POST)
        if form_data.is_valid():
            engagement_name = form_data.cleaned_data["engagement_name"]
            report_objs = Report.objects.filter(report_for__istartswith=engagement_name)
            if report_objs:
                report_obj = report_objs.first()
                engagement_groups = report_obj.findings.all()
                if engagement_groups:
                    for eng_group in engagement_groups:
                        findings = eng_group.findings.all().filter(Name__icontains="service detection", Port__isnull=False).annotate(
                            int_port=Cast('Port', IntegerField())
                        ).values_list("Protocol", "Port")
                        if findings:
                            results.extend(findings)
    if results:
        count_tuples=dict()
        for i in results:
            if i not in count_tuples:
                count_tuples[i]=1
            else:
                count_tuples[i]+=1
        results = dict(Counter(results).most_common())
    else:
        results = {}
    return render(request, "list_services.html", {'formset': form, 'results': results})


def add_finding(request):
    ScreenshotFormSet = modelformset_factory(
        FindingScreenshot,
        form=FindingScreenshotForm,
        extra=1,  # Start with one blank form
        can_delete=True
    )
    
    if request.method == "POST":
        finding_form = FindingForm(request.POST)
        screenshot_formset = ScreenshotFormSet(
            request.POST, request.FILES,
            queryset=FindingScreenshot.objects.none()
        )
        if finding_form.is_valid() and screenshot_formset.is_valid():
            finding = finding_form.save()
            for form in screenshot_formset.cleaned_data:
                # Each form's cleaned_data will be an empty dict if the form was left blank
                if form and not form.get('DELETE', False):
                    screenshot = form.get('finding_screenshot')
                    subtle = form.get('finding_subtle', '')
                    if screenshot:  # Only create if a file was uploaded
                        screenshot_obj = FindingScreenshot.objects.create(
                            finding_subtle=subtle,
                            finding_screenshot=screenshot
                        )
                        finding.screenshots.add(screenshot_obj)
            return redirect("add_finding")  # Change to your desired redirect URL
    else:
        finding_form = FindingForm()
        screenshot_formset = ScreenshotFormSet(queryset=FindingScreenshot.objects.none())
        
    context = {
        "finding_form": finding_form,
        "screenshot_formset": screenshot_formset,
    }
    return render(request, "finding/add_finding.html", context)


class FindingListView(ListView):
    model = Finding
    template_name = "finding/list_findings.html"
    context_object_name = "findings"


class FindingUpdateView(UpdateView):
    model = Finding
    form_class = FindingForm
    template_name = "finding/edit_finding.html"
    success_url = reverse_lazy("list_findings")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ScreenshotFormSet = modelformset_factory(
            FindingScreenshot,
            form=FindingScreenshotForm,
            extra=1,
            can_delete=True
        )
        screenshots_qs = self.object.screenshots.all()
        if self.request.method == "POST":
            context["screenshot_formset"] = ScreenshotFormSet(
                self.request.POST,
                self.request.FILES,
                queryset=screenshots_qs,
                prefix="screenshots"
            )
        else:
            context["screenshot_formset"] = ScreenshotFormSet(
                queryset=screenshots_qs,
                prefix="screenshots"
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        screenshot_formset = context["screenshot_formset"]
        self.object = form.save()
        if screenshot_formset.is_valid():
            for sform in screenshot_formset.deleted_forms:
                screenshot_id = sform.cleaned_data.get("id")
                if isinstance(screenshot_id, FindingScreenshot):
                    screenshot_id = screenshot_id.pk
                if screenshot_id:
                    screenshot_instance = FindingScreenshot.objects.filter(id=screenshot_id).first()
                    if screenshot_instance:
                        print(f"Deleting Screenshot {screenshot_instance.pk}")
                        self.object.screenshots.remove(screenshot_instance)
                        screenshot_instance.delete()
            for sform in screenshot_formset:
                if sform.cleaned_data and not sform.cleaned_data.get("DELETE"):
                    screenshot = sform.save(commit=False)
                    if not screenshot.pk:
                        screenshot.save()
                    self.object.screenshots.add(screenshot)
        return redirect(self.success_url)


class ReportCreateView(CreateView):
    model = Report
    form_class = ReportForm
    template_name = "reports/create_report.html"
    success_url = reverse_lazy("report_list")

class ReportListView(ListView):
    model = Report
    template_name = "reports/report_list.html"
    context_object_name = "reports"

class ReportEditView(UpdateView):
    model = Report
    form_class = ReportForm
    template_name = "reports/edit_report.html"
    success_url = reverse_lazy("report_list")

class GenerateReportView(FormView):
    template_name = "reports/generate_report.html"
    form_class = GenerateReportForm
    success_url = reverse_lazy("report_list")

    def get_form(self, form_class=None):
        """Customize form to only show active reports."""
        form = super().get_form(form_class)
        form.fields["reports"].queryset = Report.objects.all()
        return form

    def form_valid(self, form):
        report_type = form.cleaned_data["report_type"]
        selected_reports = form.cleaned_data["reports"]

        if not selected_reports.exists():
            messages.error(self.request, "No reports selected!")
            return self.form_invalid(form)

        response = generate_report_type(selected_reports, report_type)
        return response  # Return the generated file as a download

# ClientContact
class ClientContactListView(ListView):
    model = ClientContact
    template_name = "contacts/clientcontact_list.html"
    context_object_name = "clientcontacts"

class ClientContactUpdateView(UpdateView):
    model = ClientContact
    form_class = ClientContactForm
    template_name = "contacts/edit_clientcontact.html"
    success_url = reverse_lazy("clientcontact_list")

class ClientContactCreateView(CreateView):
    model = ClientContact
    form_class = ClientContactForm
    template_name = "contacts/create_clientcontact.html"
    success_url = reverse_lazy("clientcontact_list")

# RTContact
class RTContactListView(ListView):
    model = RTContact
    template_name = "contacts/rtcontact_list.html"
    context_object_name = "rtcontacts"

class RTContactUpdateView(UpdateView):
    model = RTContact
    form_class = RTContactForm
    template_name = "contacts/edit_rtcontact.html"
    success_url = reverse_lazy("rtcontact_list")

class RTContactCreateView(CreateView):
    model = RTContact
    form_class = RTContactForm
    template_name = "contacts/create_rtcontact.html"
    success_url = reverse_lazy("rtcontact_list")

# Strength
class StrengthListView(ListView):
    model = Strength
    template_name = "strengths/strength_list.html"
    context_object_name = "strengths"

class StrengthUpdateView(UpdateView):
    model = Strength
    form_class = StrengthForm
    template_name = "strengths/edit_strength.html"
    success_url = reverse_lazy("strength_list")

class StrengthCreateView(CreateView):
    model = Strength
    form_class = StrengthForm
    template_name = "strengths/create_strength.html"
    success_url = reverse_lazy("strength_list")

# Improvement
class ImprovementListView(ListView):
    model = Improvement
    template_name = "improvements/improvement_list.html"
    context_object_name = "improvements"

class ImprovementUpdateView(UpdateView):
    model = Improvement
    form_class = ImprovementForm
    template_name = "improvements/edit_improvement.html"
    success_url = reverse_lazy("improvement_list")

class ImprovementCreateView(CreateView):
    model = Improvement
    form_class = ImprovementForm
    template_name = "improvements/create_improvement.html"
    success_url = reverse_lazy("improvement_list")

# SolutionOverride
class SolutionOverrideListView(ListView):
    model = SolutionOverride
    template_name = "overrides/solutionoverride_list.html"
    context_object_name = "solutionoverrides"

class SolutionOverrideCreateView(CreateView):
    model = SolutionOverride
    form_class = SolutionOverrideForm
    template_name = "overrides/create_solutionoverride.html"
    success_url = reverse_lazy("solutionoverride_list")

class SolutionOverrideUpdateView(UpdateView):
    model = SolutionOverride
    form_class = SolutionOverrideForm
    template_name = "overrides/edit_solutionoverride.html"
    success_url = reverse_lazy("solutionoverride_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create a formset for handling multiple screenshots with deletion
        ScreenshotFormSet = modelformset_factory(
            FindingScreenshot,
            form=FindingScreenshotForm,
            extra=1,  # Allow adding new screenshots
            can_delete=True  # Allow deleting existing screenshots
        )

        # Query existing screenshots related to the SolutionOverride
        screenshots_qs = self.object.screenshots.all()

        if self.request.method == "POST":
            context["screenshot_formset"] = ScreenshotFormSet(
                self.request.POST,
                self.request.FILES,
                queryset=screenshots_qs,
                prefix="screenshots"
            )
        else:
            context["screenshot_formset"] = ScreenshotFormSet(
                queryset=screenshots_qs,
                prefix="screenshots"
            )

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        screenshot_formset = context["screenshot_formset"]
        self.object = form.save()

        if screenshot_formset.is_valid():
            # Process deletions
            for sform in screenshot_formset.deleted_forms:
                if sform.instance.pk:
                    self.object.screenshots.remove(sform.instance)  # Unlink ManyToMany
                    sform.instance.delete()  # Delete actual screenshot

            # Process new or updated screenshots
            for sform in screenshot_formset:
                if sform.cleaned_data and not sform.cleaned_data.get("DELETE"):
                    screenshot = sform.save(commit=False)

                    if not screenshot.pk:
                        screenshot.save()  # Save first to get an ID

                    self.object.screenshots.add(screenshot)  # Link to ManyToMany

        else:
            print("Screenshot formset errors:", screenshot_formset.errors)

        return redirect(self.success_url)

# ScoreOverride
class ScoreOverrideListView(ListView):
    model = ScoreOverride
    template_name = "overrides/scoreoverride_list.html"
    context_object_name = "scoreoverrides"

class ScoreOverrideUpdateView(UpdateView):
    model = ScoreOverride
    form_class = ScoreOverrideForm
    template_name = "overrides/edit_scoreoverride.html"
    success_url = reverse_lazy("scoreoverride_list")

class ScoreOverrideCreateView(CreateView):
    model = ScoreOverride
    form_class = ScoreOverrideForm
    template_name = "overrides/create_scoreoverride.html"
    success_url = reverse_lazy("scoreoverride_list")