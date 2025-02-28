from django import forms
from reportgen.models import (
    Finding,
    FindingScreenshot,
    Report,
    ClientContact,
    RTContact,
    ScoreOverride,
    Strength,
    Improvement,
    SolutionOverride,
)


class UniqueFindingForm(forms.Form):
    engagement_name = forms.CharField(label="Report Name: ", max_length=100)

class FindingForm(forms.ModelForm):
    class Meta:
        model = Finding
        fields = [
            "nessus_scan_name",
            "Name",
            "Host",
            "Protocol",
            "Port",
            "CVSS_v3_0_Base_Score",
            "CVE",
            "Synopsis",
            "Description",
            "Solution",
            "See_Also",
        ]
        labels = {
            "nessus_scan_name": "Engagement Name",
            "Name": "Finding Title",
            "Synopsis": "Impact",
            "Solution": "Recommendations",
            "See_Also": "Sources & Reference Links"
        }

class FindingScreenshotForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = FindingScreenshot
        fields = ["id", "finding_subtle", "finding_screenshot"]

class ReportForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'}
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'}
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Report
        fields = [
            "reporting_team",
            "report_for",
            "test_type",
            "start_date",
            "end_date",
            "client_contacts",
            "rt_contacts",
            "scope_internal",
            "scope_external",
            "scope_wifi",
            "special_considerations",
            "strengths",
            "improvement_areas",
            "test_from",
            "compromise_success",
            "risk_level",
            "filter_to_scores",
            "findings",
            "score_overrides",
            "solution_overrides",
        ]
        labels = {
            "report_for": "Reporting Team",
            "report_for": "Report For",
            "test_type": "Test Type",
            "start_date": "Start Date",
            "end_date": "End Date",
            "client_contacts": "Client Contacts",
            "rt_contacts": "RT Contacts",
            "scope_internal": "Internal Scope",
            "scope_external": "External Scope",
            "scope_wifi": "WiFi Scope",
            "special_considerations": "Special Considerations",
            "strengths": "Strengths",
            "improvement_areas": "Improvement Areas",
            "test_from": "Test From",
            "compromise_success": "Compromise Success",
            "risk_level": "Risk Level",
            "filter_to_scores": "Filter to Scores",
            "findings": "Findings",
            "score_overrides": "Score Overrides",
            "solution_overrides": "Solution Overrides",
        }

class ClientContactForm(forms.ModelForm):
    class Meta:
        model = ClientContact
        fields = ["client_name", "client_contact"]

class RTContactForm(forms.ModelForm):
    class Meta:
        model = RTContact
        fields = ["rt_name", "rt_contact"]

class ScoreOverrideForm(forms.ModelForm):
    class Meta:
        model = ScoreOverride
        fields = ["score_override_name", "score_override_value"]

class StrengthForm(forms.ModelForm):
    class Meta:
        model = Strength
        fields = ["strength_subtle", "strength_screenshot"]

class ImprovementForm(forms.ModelForm):
    class Meta:
        model = Improvement
        fields = ["improvement_subtle", "improvement_screenshot"]

class SolutionOverrideForm(forms.ModelForm):
    class Meta:
        model = SolutionOverride
        fields = [
            "vulnerability_title", 
            "solution_body", 
            "see_also", 
            # "screenshots"
        ]

class GenerateReportForm(forms.Form):
    REPORT_TYPE_CHOICES = [
        ("executive", "Executive Report"),
        ("verbose", "Detailed Report with Evidence"),
        ("detailed", "Detailed Report"),
    ]
    
    report_type = forms.ChoiceField(choices=REPORT_TYPE_CHOICES, required=True, label="Select Report Type")
    reports = forms.ModelMultipleChoiceField(
        queryset=Report.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Reports to Generate"
    )
