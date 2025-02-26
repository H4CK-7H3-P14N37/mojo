from django.db import models
from django.db.models import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator

# TODO: add model to override solutions with screenshots model as well

class FindingScreenshot(models.Model):
    finding_subtle = models.TextField()
    finding_screenshot = models.ImageField(upload_to='findings/')

    def __str__(self):
        return self.finding_subtle

    class Meta:
        verbose_name = 'Finding Screenshot'
        verbose_name_plural = 'Finding Screenshot'


class Finding(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True)
    nessus_scan_name = models.CharField(
        max_length=190,
        null=False,
        blank=False,
        db_index=True,
    )
    screenshots = models.ManyToManyField(FindingScreenshot, blank=True)
    Plugin_ID = models.TextField(null=True, blank=True)
    CVE = models.TextField(null=True, blank=True)
    CVSS_v2_0_Base_Score = models.TextField(null=True, blank=True)
    Risk = models.TextField(null=True, blank=True)
    Host = models.TextField(null=True, blank=True)
    Protocol = models.TextField(null=True, blank=True)
    Port = models.TextField(null=True, blank=True)
    Name = models.TextField(null=True, blank=True)
    Synopsis = models.TextField(null=True, blank=True)
    Description = models.TextField(null=True, blank=True)
    Solution = models.TextField(null=True, blank=True)
    See_Also = models.TextField(null=True, blank=True)
    Plugin_Output = models.TextField(null=True, blank=True)
    STIG_Severity = models.TextField(null=True, blank=True)
    CVSS_v3_0_Base_Score = models.TextField(null=True, blank=True)
    CVSS_v2_0_Temporal_Score = models.TextField(null=True, blank=True)
    CVSS_v3_0_Temporal_Score = models.TextField(null=True, blank=True)
    VPR_Score = models.TextField(null=True, blank=True)
    Risk_Factor = models.TextField(null=True, blank=True)
    BID = models.TextField(null=True, blank=True)
    XREF = models.TextField(null=True, blank=True)
    MSKB = models.TextField(null=True, blank=True)
    Plugin_Publication_Date = models.TextField(null=True, blank=True)
    Plugin_Modification_Date = models.TextField(null=True, blank=True)
    Metasploit = models.TextField(null=True, blank=True)
    Core_Impact = models.TextField(null=True, blank=True)
    CANVAS = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Finding, self).save(*args, **kwargs)
        # Ensure each finding is grouped by its Nessus scan name
        nessus_title = self.nessus_scan_name
        obj, _ = EngagementFindingGroup.objects.get_or_create(engagement_name=nessus_title)
        obj.findings.add(self.id)
        obj.save()

    def __str__(self):
        return f'{self.nessus_scan_name} - {self.Name}'

    class Meta:
        verbose_name = 'Findings'
        verbose_name_plural = 'Findings'


class EngagementFindingGroup(models.Model):
    engagement_name = models.CharField(max_length=190, null=False, blank=False, db_index=True)
    findings = models.ManyToManyField(Finding)

    def get_queryset(self, request):
        model_qs = super(EngagementFindingGroup, self).get_queryset(request)
        model_qs = model_qs.prefetch_related('findings')
        return model_qs

    def __str__(self):
        return self.engagement_name

    class Meta:
        verbose_name = 'Engagement Findings Group'
        verbose_name_plural = 'Engagement Findings Group'


class TestType(models.Model):
    test_name = models.CharField(max_length=190, null=False, blank=False, db_index=True)
    test_value = models.CharField(max_length=190, null=False, blank=False, db_index=True)

    def __str__(self):
        return self.test_name

    class Meta:
        verbose_name = 'Test Types'
        verbose_name_plural = 'Test Types'


class ClientContact(models.Model):
    client_name = models.CharField(max_length=190, null=False, blank=False, db_index=True)
    client_contact = models.TextField()

    def __str__(self):
        return self.client_name

    class Meta:
        verbose_name = 'Client Contacts'
        verbose_name_plural = 'Client Contacts'


class RTContact(models.Model):
    rt_name = models.CharField(max_length=190, null=False, blank=False, db_index=True)
    rt_contact = models.TextField()

    def __str__(self):
        return self.rt_name

    class Meta:
        verbose_name = 'RT Contacts'
        verbose_name_plural = 'RT Contacts'


class TestFrom(models.Model):
    test_from_name = models.CharField(max_length=190, null=False, blank=False, db_index=True)
    test_from_value = models.CharField(max_length=190, null=False, blank=False, db_index=True)

    def __str__(self):
        return self.test_from_name

    class Meta:
        verbose_name = 'Test From Types'
        verbose_name_plural = 'Test From Types'


class RiskLevel(models.Model):
    risk_level_name = models.CharField(max_length=190, null=False, blank=False, db_index=True)
    risk_matrix_row = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    risk_matrix_col = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )

    def __str__(self):
        return f'{self.risk_level_name} - {self.risk_matrix_col} - {self.risk_matrix_row}'

    class Meta:
        verbose_name = 'Risk Levels'
        verbose_name_plural = 'Risk Levels'


class ScoreOverride(models.Model):
    score_override_name = models.CharField(max_length=190, null=False, blank=False, db_index=True)
    score_override_value = models.FloatField(
        default=10.0,
        validators=[
            MaxValueValidator(10.0),
            MinValueValidator(0.0)
        ]
    )

    def __str__(self):
        return f'{self.score_override_name} - {self.score_override_value}'

    class Meta:
        verbose_name = 'Score Overrides'
        verbose_name_plural = 'Score Overrides'


class Strength(models.Model):
    strength_subtle = models.TextField()
    strength_screenshot = models.ImageField(upload_to='strengths/', blank=True)

    def __str__(self):
        return self.strength_subtle

    class Meta:
        verbose_name = 'Strengths'
        verbose_name_plural = 'Strengths'


class Improvement(models.Model):
    improvement_subtle = models.TextField()
    improvement_screenshot = models.ImageField(upload_to='improvements/', blank=True)

    def __str__(self):
        return self.improvement_subtle

    class Meta:
        verbose_name = 'Improvements'
        verbose_name_plural = 'Improvements'


class SolutionOverride(models.Model):
    vulnerability_title = models.TextField(null=False, blank=False, default='')
    solution_body = models.TextField(null=False, blank=False, default='')
    see_also = models.TextField(null=True, blank=True, default='')
    screenshots = models.ManyToManyField(FindingScreenshot, blank=True)

    def __str__(self):
        return self.vulnerability_title

    class Meta:
        verbose_name = 'Solution Overrides'
        verbose_name_plural = 'Solution Overrides'


class Report(models.Model):
    report_for = models.CharField(max_length=190, null=False, blank=False, db_index=True)
    test_type = models.ForeignKey(TestType, on_delete=models.PROTECT)
    start_date = models.DateTimeField(null=False, blank=False)
    end_date = models.DateTimeField(null=False, blank=False)
    client_contacts = models.ManyToManyField(ClientContact)
    rt_contacts = models.ManyToManyField(RTContact)
    scope_internal = models.TextField(null=True, blank=True)
    scope_external = models.TextField(null=True, blank=True)
    scope_wifi = models.TextField(null=True, blank=True)
    special_considerations = models.TextField(null=True, blank=True)
    strengths = models.ManyToManyField(Strength)
    improvement_areas = models.ManyToManyField(Improvement)
    test_from = models.ForeignKey(TestFrom, on_delete=models.PROTECT)
    compromise_success = models.BooleanField(default=True)
    risk_level = models.ForeignKey(RiskLevel, on_delete=models.PROTECT)
    filter_to_scores = models.BooleanField(default=True)
    findings = models.ManyToManyField(EngagementFindingGroup)
    score_overrides = models.ManyToManyField(ScoreOverride, blank=True)
    solution_overrides = models.ManyToManyField(SolutionOverride, blank=True)

    def __str__(self):
        return f'{self.report_for} - {self.start_date}'

    class Meta:
        verbose_name = 'Pentest Report'
        verbose_name_plural = 'Pentest Report'


def default_json_keys():
    return {
        "url": "",
        "access_key": "",
        "secret_key": ""
    }


class NessusConfig(models.Model):
    scanner_name = models.CharField(max_length=190, null=False, blank=False, db_index=True, unique=True)
    enabled = models.BooleanField(default=True)
    scanner_config = JSONField(default=default_json_keys)

    def __str__(self):
        return self.scanner_name

    class Meta:
        verbose_name = 'Nessus Scanner Configurations'
        verbose_name_plural = 'Nessus Scanner Configurations'


class NessusImportHistory(models.Model):
    scan_id = models.IntegerField()
    history_id = models.IntegerField()
    scanner = models.ForeignKey(NessusConfig, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.scanner.scanner_name} - {self.scan_id} - {self.history_id}'

    class Meta:
        verbose_name = 'Nessus Scan Import History'
        verbose_name_plural = 'Nessus Scan Import History'
