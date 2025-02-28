# Standard library imports
import os
from wsgiref.util import FileWrapper

# Django imports
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django.http import Http404, StreamingHttpResponse
from django.db import models
from django.db.models import Q
from django.db.models.functions import Cast

# Third-party imports
from import_export import resources
from import_export.tmp_storages import CacheStorage
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from django_admin_listfilter_dropdown.filters import DropdownFilter

# Local application imports
from reportgen.models import (
    FindingScreenshot,
    Finding,
    EngagementFindingGroup,
    TestType,
    ClientContact,
    RTContact,
    TestFrom,
    RiskLevel,
    ScoreOverride,
    Strength,
    Improvement,
    Report,
    NessusConfig,
    NessusImportHistory,
    SolutionOverride,
)
from api_classes.doc_gen_api import OSSReportGen

@admin.action(
    description='Duplicate Findings',
)
def duplicate_findings(modeladmin, request, queryset):
    for obj in queryset:
        obj.id = None
        obj.nessus_scan_name = "duplicate"
        obj.save()


@admin.action(
    description='Duplicate Solutions',
)
def duplicate_solutions(modeladmin, request, queryset):
    for obj in queryset:
        obj.id = None
        obj.vulnerability_title = f"{obj.vulnerability_title} Copy"
        obj.save()


@admin.action(
    description='Duplicate Report',
)
def duplicate_report(modeladmin, request, queryset):
    for obj in queryset:
        obj.id = None
        obj.report_for = f"{obj.report_for} Copy"
        obj.save()


def generate_report_type(queryset, report_type):
    try:
        if not os.path.exists(settings.PT_REPORT_DIR):
            os.makedirs(settings.PT_REPORT_DIR)
        obj = OSSReportGen(save_dir=settings.PT_REPORT_DIR)
        report_obj = queryset.first()
        if report_obj:
            client_contacts = [
                cobj.replace(
                    "\r",
                    "") for cobj in report_obj.client_contacts.all().values_list(
                    "client_contact",
                    flat=True)]
            rt_contact = [
                cobj.replace(
                    "\r",
                    "") for cobj in report_obj.rt_contacts.all().values_list(
                    "rt_contact",
                    flat=True)]
            vuln_dict_list = []
            engagement_objs = report_obj.findings.all()
            if engagement_objs:
                for engagement_obj in engagement_objs:
                    engagement_findings_objs = engagement_obj.findings.all()
                    if engagement_findings_objs:
                        for finding_obj in engagement_findings_objs:
                            finding_tmp_dict = finding_obj.__dict__
                            finding_screenshot_objs = finding_obj.screenshots.values(
                                "finding_subtle", "finding_screenshot")
                            findings_screenshot_dict_list = []
                            if finding_screenshot_objs:
                                for finding_screenshot_obj in finding_screenshot_objs:
                                    tmp_screen_dict = {
                                        'finding_subtle': finding_screenshot_obj.get('finding_subtle'),
                                        'finding_screenshot': os.path.join(
                                            settings.MEDIA_ROOT,
                                            finding_screenshot_obj.get('finding_screenshot'))}
                                    findings_screenshot_dict_list.append(
                                        tmp_screen_dict)
                            finding_tmp_dict.update({
                                "finding_screenshots": findings_screenshot_dict_list
                            })
                            vuln_dict_list.append(finding_tmp_dict)
            score_override_dict = {}
            score_override_objs = report_obj.score_overrides.all()
            if score_override_objs:
                for score_override_obj in score_override_objs:
                    score_override_dict.update({
                        score_override_obj.score_override_name: score_override_obj.score_override_value
                    })
            strengths_list = []
            strength_objs = report_obj.strengths.all()
            if strength_objs:
                for strength_obj in strength_objs:
                    if strength_obj.strength_screenshot:
                        tmp_strength_dict = {
                            'strength_subtle': strength_obj.strength_subtle.replace(
                                "\r", "").replace(
                                "\n", ""), 'strength_screenshot': os.path.join(
                                settings.MEDIA_ROOT, strength_obj.strength_screenshot.path)}
                    else:
                        tmp_strength_dict = {
                            'strength_subtle': strength_obj.strength_subtle.replace(
                                "\r", "").replace(
                                "\n", ""), 'strength_screenshot': ""}
                    strengths_list.append(tmp_strength_dict)

            improvements_list = []
            improvement_objs = report_obj.improvement_areas.all()
            if improvement_objs:
                for improvement_obj in improvement_objs:
                    if improvement_obj.improvement_screenshot:
                        tmp_improvement_dict = {
                            'improvement_subtle': improvement_obj.improvement_subtle.replace(
                                "\r", "").replace(
                                "\n", ""), 'improvement_screenshot': os.path.join(
                                settings.MEDIA_ROOT, improvement_obj.improvement_screenshot.path)}
                    else:
                        tmp_improvement_dict = {
                            'improvement_subtle': improvement_obj.improvement_subtle.replace(
                                "\r", "").replace(
                                "\n", ""), 'improvement_screenshot': ""}
                    improvements_list.append(tmp_improvement_dict)
            scope_external_list = []
            if report_obj.scope_external:
                for scope in report_obj.scope_external.replace(
                        "\r", "").split("\n"):
                    if scope:
                        scope_external_list.append(scope)

            scope_internal_list = []
            if report_obj.scope_internal:
                for scope in report_obj.scope_internal.replace(
                        "\r", "").split("\n"):
                    if scope:
                        scope_internal_list.append(scope)

            scope_wifi_list = []
            if report_obj.scope_wifi:
                for scope in report_obj.scope_wifi.replace(
                        "\r", "").split("\n"):
                    if scope:
                        scope_wifi_list.append(scope)

            solutions_override_dict = {}
            solutions_override_objs = report_obj.solution_overrides.all()
            if solutions_override_objs:
                for solutions_obj in solutions_override_objs:
                    solution_screenshot_objs = solutions_obj.screenshots.values(
                        "finding_subtle", "finding_screenshot")
                    tmp_list = []
                    if solution_screenshot_objs:
                        for solution_screenshot_obj in solution_screenshot_objs:
                            tmp_screen_dict = {
                                'finding_subtle': solution_screenshot_obj.get('finding_subtle'),
                                'finding_screenshot': os.path.join(
                                    settings.BASE_DIR,
                                    solution_screenshot_obj.get('finding_screenshot'))}
                            tmp_list.append(tmp_screen_dict)
                    solutions_override_dict.update({
                        solutions_obj.vulnerability_title: {
                            "solution_text": solutions_obj.solution_body,
                            "solution_see_also": solutions_obj.see_also,
                            "screenshots": tmp_list
                        }
                    })

            if report_type.lower() == "executive":
                filename_returned = obj.generate_doc(
                    REPORTING_TEAM=report_obj.reporting_team,
                    REPORT_FOR=report_obj.report_for,
                    TITLE_MONTH_YEAR=report_obj.start_date.strftime("%B %Y"),
                    TEST_TYPE=report_obj.test_type.test_value,
                    START_DATE=report_obj.start_date.strftime("%d %B %Y"),
                    END_DATE=report_obj.end_date.strftime("%d %B %Y"),
                    CLIENT_CONTACT_DATA=list(client_contacts),
                    RT_CONTACT_DATA=list(rt_contact),
                    SCOPE_INTERNAL=scope_internal_list,
                    SCOPE_EXTERNAL=scope_external_list,
                    WIFI_SCOPE=scope_wifi_list,
                    SCOPE_TEST_FROM=report_obj.test_from.test_from_value,
                    COMPROMISE_SUCCESS=report_obj.compromise_success,
                    RISK_LEVEL=report_obj.risk_level.risk_level_name,
                    RISK_MATRIX_ROW=report_obj.risk_level.risk_matrix_row,
                    RISK_MATRIX_COL=report_obj.risk_level.risk_matrix_col,
                    VULN_LIST=vuln_dict_list,
                    filter_to_scores=report_obj.filter_to_scores,
                    ip_strip=True,
                    score_overrides_dict=score_override_dict,
                    strength_list=strengths_list,
                    improvements_list=improvements_list,
                    with_evidence=False,
                    SPECIAL_CONSIDERATIONS=report_obj.special_considerations,
                    solutions_override_dict=solutions_override_dict
                )
            elif report_type.lower() == "verbose":
                filename_returned = obj.generate_doc(
                    REPORTING_TEAM=report_obj.reporting_team,
                    REPORT_FOR=report_obj.report_for,
                    TITLE_MONTH_YEAR=report_obj.start_date.strftime("%B %Y"),
                    TEST_TYPE=report_obj.test_type.test_value,
                    START_DATE=report_obj.start_date.strftime("%d %B %Y"),
                    END_DATE=report_obj.end_date.strftime("%d %B %Y"),
                    CLIENT_CONTACT_DATA=list(client_contacts),
                    RT_CONTACT_DATA=list(rt_contact),
                    SCOPE_INTERNAL=scope_internal_list,
                    SCOPE_EXTERNAL=scope_external_list,
                    WIFI_SCOPE=scope_wifi_list,
                    SCOPE_TEST_FROM=report_obj.test_from.test_from_value,
                    COMPROMISE_SUCCESS=report_obj.compromise_success,
                    RISK_LEVEL=report_obj.risk_level.risk_level_name,
                    RISK_MATRIX_ROW=report_obj.risk_level.risk_matrix_row,
                    RISK_MATRIX_COL=report_obj.risk_level.risk_matrix_col,
                    VULN_LIST=vuln_dict_list,
                    filter_to_scores=report_obj.filter_to_scores,
                    score_overrides_dict=score_override_dict,
                    ip_strip=False,
                    strength_list=strengths_list,
                    improvements_list=improvements_list,
                    with_evidence=True,
                    SPECIAL_CONSIDERATIONS=report_obj.special_considerations,
                    solutions_override_dict=solutions_override_dict
                )
            else:
                filename_returned = obj.generate_doc(
                    REPORTING_TEAM=report_obj.reporting_team,
                    REPORT_FOR=report_obj.report_for,
                    TITLE_MONTH_YEAR=report_obj.start_date.strftime("%B %Y"),
                    TEST_TYPE=report_obj.test_type.test_value,
                    START_DATE=report_obj.start_date.strftime("%d %B %Y"),
                    END_DATE=report_obj.end_date.strftime("%d %B %Y"),
                    CLIENT_CONTACT_DATA=list(client_contacts),
                    RT_CONTACT_DATA=list(rt_contact),
                    SCOPE_INTERNAL=scope_internal_list,
                    SCOPE_EXTERNAL=scope_external_list,
                    WIFI_SCOPE=scope_wifi_list,
                    SCOPE_TEST_FROM=report_obj.test_from.test_from_value,
                    COMPROMISE_SUCCESS=report_obj.compromise_success,
                    RISK_LEVEL=report_obj.risk_level.risk_level_name,
                    RISK_MATRIX_ROW=report_obj.risk_level.risk_matrix_row,
                    RISK_MATRIX_COL=report_obj.risk_level.risk_matrix_col,
                    VULN_LIST=vuln_dict_list,
                    filter_to_scores=report_obj.filter_to_scores,
                    score_overrides_dict=score_override_dict,
                    strength_list=strengths_list,
                    improvements_list=improvements_list,
                    with_evidence=False,
                    SPECIAL_CONSIDERATIONS=report_obj.special_considerations,
                    solutions_override_dict=solutions_override_dict
                )
            chunk_size = 1024
            if os.path.exists(filename_returned):
                response = StreamingHttpResponse(
                    FileWrapper(open(filename_returned, 'rb'), chunk_size),
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                response['Content-Disposition'] = "attachment; filename={0}".format(
                    os.path.basename(filename_returned))
                response['Content-Length'] = os.path.getsize(filename_returned)
                return response
    except Exception as e:
        print(e)
    raise Http404


@admin.action(
    description='Generate Detailed Report',
)
def generate_report(modeladmin, request, queryset):
    return generate_report_type(
        queryset,
        report_type=""
    )


@admin.action(
    description='Generate Detailed Report with Evidence',
)
def generate_report_evidence(modeladmin, request, queryset):
    return generate_report_type(
        queryset,
        report_type="verbose"
    )


@admin.action(
    description='Generate Executive Report',
)
def generate_exec_report(modeladmin, request, queryset):
    return generate_report_type(
        queryset,
        report_type="executive"
    )


@admin.action(
    description='Remove PCI DSS Findings',
)
def remove_pci_findings(modeladmin, request, queryset):
    _ = queryset.filter(Name__startswith="PCI DSS Compliance").delete()


@admin.action(
    description='Remove OpenSSH False Positive Findings',
)
def remove_openssh_false_postives(modeladmin, request, queryset):
    _ = queryset.filter(
        Q(Name="OpenSSH PCI Disputed Vulnerabilities") |
        Q(Name="OPIE w/ OpenSSH Account Enumeration") |
        Q(Name="SSH Server CBC Mode Ciphers Enabled") |
        Q(Name="SSH Weak MAC Algorithms Enabled") |
        Q(Name="SSH Weak Algorithms Supported") |
        Q(Name="SSH Weak Key Exchange Algorithms Enabled") |
        Q(Name="SSH Protocol Version 1 Session Key Retrieval") |
        Q(Name="SSH SHA-1 HMAC Algorithms Enabled (PCI DSS)") |
        Q(Name="OpenSSH PCI Disputed Vulnerabilities.") |
        Q(Name__startswith="OpenSSH >= ", Name__endswith="AllowTcpForwarding Port Bouncing")
    ).delete()


@admin.action(
    description='Remove SSL/TLS Duplicated Findings',
)
def remove_duplicate_ssl_tls(modeladmin, request, queryset):
    _ = queryset.filter(
        Q(Name="SSL/TLS Protocol Initialization Vector Implementation Information Disclosure Vulnerability (BEAST)") |
        Q(Name="SSL/TLS Diffie-Hellman Modulus <= 1024 Bits (Logjam)") |
        Q(Name="SSL/TLS Services Support RC4 (PCI DSS)") |
        Q(Name="TLS Version 1.1 Protocol Detection (PCI DSS)") |
        Q(Name="SSL Medium Strength Cipher Suites Supported (SWEET32)") |
        Q(Name="SSL Self-Signed Certificate") |
        Q(Name="SSLv3 Padding Oracle On Downgraded Legacy Encryption Vulnerability (POODLE)") |
        Q(Name="SSL RC4 Cipher Suites Supported (Bar Mitzvah)") |
        Q(Name="SSL 64-bit Block Size Cipher Suites Supported (SWEET32)") |
        Q(Name__startswith="TLS Version", Port=3389)
    ).delete()


@admin.action(
    description='Remove Nonaction Findings',
)
def remove_nonaction_findings(modeladmin, request, queryset):
    _ = queryset.filter(
        Q(Name="Microsoft ASP.NET ValidateRequest Filters Bypass") |
        Q(Name="Microsoft ASP.NET MS-DOS Device Name DoS (PCI-DSS check)") |
        Q(Name="ICMP Timestamp Request Remote Date Disclosure") |
        Q(Name="OS vulnerabilities detected in banner reporting (PCI-DSS check)") |
        Q(Name="mDNS Detection (Remote Network)") |
        Q(Name="Script Src Integrity Check") |
        Q(Name__startswith="JQuery ", Name__endswith="Multiple XSS")
    ).delete()


class ImportNessusForm(ActionForm):
    file_input = forms.FileField()


class CVSSFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ('CVSS Filter')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'cvss'

    def lookups(self, request, model_admin):
        return (
            ('hc', ('High & Critical')),
            ('mhc', ('Medium, High, & Critical')),
            ('lmhc', ('With Score')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'hc':
            return queryset.annotate(
                cvss2_integer=Cast('CVSS_v2_0_Base_Score', output_field=models.IntegerField()),
                cvss3_integer=Cast('CVSS_v3_0_Base_Score', output_field=models.IntegerField())
            ).filter(Q(cvss2_integer__gte=7.0) | Q(cvss3_integer__gte=7.0))
        if self.value() == 'mhc':
            return queryset.annotate(
                cvss2_integer=Cast('CVSS_v2_0_Base_Score', output_field=models.IntegerField()),
                cvss3_integer=Cast('CVSS_v3_0_Base_Score', output_field=models.IntegerField())
            ).filter(Q(cvss2_integer__gte=4.0) | Q(cvss3_integer__gte=4.0))
        if self.value() == 'lmhc':
            return queryset.annotate(
                cvss2_integer=Cast('CVSS_v2_0_Base_Score', output_field=models.IntegerField()),
                cvss3_integer=Cast('CVSS_v3_0_Base_Score', output_field=models.IntegerField())
            ).filter(Q(cvss2_integer__gte=0.1) | Q(cvss3_integer__gte=0.1))


class FindingResource(resources.ModelResource):
    Plugin_ID = Field(attribute='Plugin_ID', column_name='Plugin ID')
    CVE = Field(attribute='CVE', column_name='CVE')
    CVSS_v2_0_Base_Score = Field(
        attribute='CVSS_v2_0_Base_Score',
        column_name='CVSS v2.0 Base Score')
    Risk = Field(attribute='Risk', column_name='Risk')
    Host = Field(attribute='Host', column_name='Host')
    Protocol = Field(attribute='Protocol', column_name='Protocol')
    Port = Field(attribute='Port', column_name='Port')
    Name = Field(attribute='Name', column_name='Name')
    Synopsis = Field(attribute='Synopsis', column_name='Synopsis')
    Description = Field(attribute='Description', column_name='Description')
    Solution = Field(attribute='Solution', column_name='Solution')
    See_Also = Field(attribute='See_Also', column_name='See Also')
    Plugin_Output = Field(
        attribute='Plugin_Output',
        column_name='Plugin Output')
    STIG_Severity = Field(
        attribute='STIG_Severity',
        column_name='STIG Severity')
    CVSS_v3_0_Base_Score = Field(
        attribute='CVSS_v3_0_Base_Score',
        column_name='CVSS v3.0 Base Score')
    CVSS_v2_0_Temporal_Score = Field(
        attribute='CVSS_v2_0_Temporal_Score',
        column_name='CVSS v2.0 Temporal Score')
    CVSS_v3_0_Temporal_Score = Field(
        attribute='CVSS_v3_0_Temporal_Score',
        column_name='CVSS v3.0 Temporal Score')
    Risk_Factor = Field(attribute='Risk_Factor', column_name='Risk Factor')
    VPR_Score = Field(attribute='VPR_Score', column_name='VPR Score')
    BID = Field(attribute='BID', column_name='BID')
    XREF = Field(attribute='XREF', column_name='XREF')
    MSKB = Field(attribute='MSKB', column_name='MSKB')
    Plugin_Publication_Date = Field(
        attribute='Plugin_Publication_Date',
        column_name='Plugin Publication Date')
    Plugin_Modification_Date = Field(
        attribute='Plugin_Modification_Date',
        column_name='Plugin Modification Date')
    Metasploit = Field(attribute='Metasploit', column_name='Metasploit')
    Core_Impact = Field(attribute='Core_Impact', column_name='Core Impact')
    CANVAS = Field(attribute='CANVAS', column_name='CANVAS')

    class Meta:
        model = Finding
        # NOTE: cant use bulk because
        # relationships with EngagementGroups wont be created
        use_bulk = False
        batch_size = 10000
        force_init_instance = True
        skip_dict = False
        skip_diff = True
        skip_html_diff = True
        import_id_fields = ['Plugin_ID', 'Host', 'Protocol', 'Port', 'Name']
        fields = (
            "Plugin ID",
            "CVE",
            "CVSS_v2_0_Base_Score",
            "Risk",
            "Host",
            "Protocol",
            "Port",
            "Name",
            "Synopsis",
            "Description",
            "Solution",
            "See_Also",
            "Plugin_Output",
            "STIG_Severity",
            "CVSS_v3_0_Base_Score",
            "CVSS_v2_0_Temporal_Score",
            "CVSS_v3_0_Temporal_Score",
            "Risk_Factor",
            "VPR_Score",
            "BID",
            "XREF",
            "MSKB",
            "Plugin_Publication_Date",
            "Plugin_Modification_Date",
            "Metasploit",
            "Core_Impact",
            "CANVAS"
        )

    def after_init_instance(self, instance, new, row, **kwargs):
        file_name = kwargs.get('file_name', 'unknown')
        instance.nessus_scan_name = file_name


class ScreenshotInline(admin.TabularInline):
    model = Finding.screenshots.through


class SolutionsScreenshotInline(admin.TabularInline):
    model = SolutionOverride.screenshots.through


class FindingAdmin(ImportExportModelAdmin):
    resource_classes = [FindingResource]
    tmp_storage_class = CacheStorage
    list_display = (
        "nessus_scan_name",
        "Risk",
        "Host",
        "Protocol",
        "Port",
        "Name",
        "CVE",
        "CVSS_v2_0_Base_Score",
        "CVSS_v3_0_Base_Score"
    )
    search_fields = (
        "nessus_scan_name",
        "Risk",
        "Host",
        "Protocol",
        "Port",
        "Name",
        "CVE",
        "CVSS_v2_0_Base_Score",
        "CVSS_v3_0_Base_Score"
    )
    list_filter = (
        ("Risk", DropdownFilter),
        ("CVSS_v2_0_Base_Score", DropdownFilter),
        ("CVSS_v3_0_Base_Score", DropdownFilter),
        ("nessus_scan_name", DropdownFilter),
        ("Port", DropdownFilter),
        CVSSFilter,
    )
    # filter_horizontal = ('screenshots',)
    inlines = [ScreenshotInline]
    fields = [
        "nessus_scan_name",
        "Host",
        "Protocol",
        "Port",
        "Name",
        "Synopsis",
        "Description",
        "Solution",
        "See_Also",
        "Plugin_Output",
        "CVE",
        "CVSS_v2_0_Base_Score",
        "CVSS_v3_0_Base_Score",
    ]
    actions = [
        remove_pci_findings,
        remove_openssh_false_postives,
        remove_duplicate_ssl_tls,
        remove_nonaction_findings,
        duplicate_findings
    ]


class ReportAdmin(admin.ModelAdmin):
    def test_type(self, obj):
        return obj.test_type.test_name
    list_display = ('report_for', 'test_type', 'start_date', 'end_date')
    list_filter = ("report_for",)
    filter_horizontal = (
        'findings',
        'strengths',
        'improvement_areas',
        'score_overrides',
        'solution_overrides')
    actions = [
        generate_report,
        generate_exec_report,
        generate_report_evidence,
        duplicate_report]


class SolutionOverrideResource(resources.ModelResource):
    class Meta:
        model = SolutionOverride


class SolutionOverrideAdmin(ImportExportModelAdmin):
    resource_class = SolutionOverrideResource
    tmp_storage_class = CacheStorage
    inlines = [SolutionsScreenshotInline]
    fields = [
        "vulnerability_title",
        "solution_body",
        "see_also"
    ]
    actions = [duplicate_solutions]


class RiskLevelResource(resources.ModelResource):
    class Meta:
        model = RiskLevel


class RiskLevelAdmin(ImportExportModelAdmin):
    resource_class = RiskLevelResource
    tmp_storage_class = CacheStorage


class ScoreOverrideResource(resources.ModelResource):
    class Meta:
        model = ScoreOverride


class ScoreOverrideAdmin(ImportExportModelAdmin):
    resource_class = ScoreOverrideResource
    tmp_storage_class = CacheStorage


class TestFromResource(resources.ModelResource):
    class Meta:
        model = TestFrom


class TestFromAdmin(ImportExportModelAdmin):
    resource_class = TestFromResource
    tmp_storage_class = CacheStorage


class RTContactResource(resources.ModelResource):
    class Meta:
        model = RTContact


class RTContactAdmin(ImportExportModelAdmin):
    resource_class = RTContactResource
    tmp_storage_class = CacheStorage


class ClientContactResource(resources.ModelResource):
    class Meta:
        model = ClientContact


class ClientContactAdmin(ImportExportModelAdmin):
    resource_class = ClientContactResource
    tmp_storage_class = CacheStorage


class TestTypeResource(resources.ModelResource):
    class Meta:
        model = TestType


class TestTypeAdmin(ImportExportModelAdmin):
    resource_class = TestTypeResource
    tmp_storage_class = CacheStorage


class EngagementFindingGroupResource(resources.ModelResource):
    class Meta:
        model = EngagementFindingGroup


class FindingInline(admin.TabularInline):
    model = EngagementFindingGroup.findings.through


class EngagementFindingGroupAdmin(ImportExportModelAdmin):
    resource_class = EngagementFindingGroupResource
    tmp_storage_class = CacheStorage
    # inlines = [ FindingInline ]
    fields = [
        "engagement_name",
        "findings"
    ]
    autocomplete_fields = ('findings',)


class StrengthResource(resources.ModelResource):
    class Meta:
        model = Strength


class StrengthAdmin(ImportExportModelAdmin):
    resource_class = StrengthResource
    tmp_storage_class = CacheStorage


class ImprovementResource(resources.ModelResource):
    class Meta:
        model = Improvement


class ImprovementAdmin(ImportExportModelAdmin):
    resource_class = ImprovementResource
    tmp_storage_class = CacheStorage


class NessusConfigResource(resources.ModelResource):
    class Meta:
        model = NessusConfig


class NessusConfigAdmin(ImportExportModelAdmin):
    resource_class = NessusConfigResource
    tmp_storage_class = CacheStorage


class NessusImportHistoryResource(resources.ModelResource):
    class Meta:
        model = NessusImportHistory


class NessusImportHistoryAdmin(ImportExportModelAdmin):
    resource_class = NessusImportHistoryResource
    tmp_storage_class = CacheStorage


admin.site.register(FindingScreenshot)
admin.site.register(Finding, FindingAdmin)
admin.site.register(TestType, TestTypeAdmin)
admin.site.register(ClientContact, ClientContactAdmin)
admin.site.register(RTContact, RTContactAdmin)
admin.site.register(TestFrom, TestFromAdmin)
admin.site.register(RiskLevel, RiskLevelAdmin)
admin.site.register(ScoreOverride, ScoreOverrideAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(EngagementFindingGroup, EngagementFindingGroupAdmin)
admin.site.register(Strength, StrengthAdmin)
admin.site.register(Improvement, ImprovementAdmin)
admin.site.register(NessusConfig, NessusConfigAdmin)
admin.site.register(NessusImportHistory, NessusImportHistoryAdmin)
admin.site.register(SolutionOverride, SolutionOverrideAdmin)
