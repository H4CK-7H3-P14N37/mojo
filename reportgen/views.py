from django.shortcuts import render
from reportgen.forms import FindingForm
from reportgen.models import Report
from django.db.models import Count
from collections import Counter
from django.db.models import IntegerField
from django.db.models.functions import Cast
from itertools import chain

# Create your views here.
def unique_findings(request):
    form = FindingForm()
    results = []
    if request.method == "POST":
        form_data = FindingForm(request.POST)
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
    form = FindingForm()
    results = []
    if request.method == "POST":
        form_data = FindingForm(request.POST)
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