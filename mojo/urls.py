"""mojo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Django imports
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Local application imports
from reportgen.views import (
    unique_findings,
    list_services,
    add_finding,
    FindingListView,
    FindingUpdateView,
    ReportCreateView,
    ReportListView,
    ReportEditView,
    ClientContactListView,
    GenerateReportView,
    ClientContactUpdateView,
    RTContactListView,
    RTContactUpdateView,
    ScoreOverrideListView,
    ScoreOverrideUpdateView,
    StrengthListView,
    StrengthUpdateView,
    ImprovementListView,
    ImprovementUpdateView,
    SolutionOverrideListView,
    SolutionOverrideUpdateView,
    ClientContactCreateView,
    RTContactCreateView,
    ScoreOverrideCreateView,
    StrengthCreateView,
    ImprovementCreateView,
    SolutionOverrideCreateView,
)
from mojo.views import home


urlpatterns = [
    path('', home, name="home_page"),
    path('superdupperadmin/', admin.site.urls, name="admin_page"),
    path('unique_findings/', unique_findings, name="unique_findings"),
    path('list_services/', list_services, name="list_services"),
    # Findings
    path('findings/', FindingListView.as_view(), name='list_findings'),
    path('finding/add/', add_finding, name='add_finding'),
    path('findings/edit/<int:pk>/', FindingUpdateView.as_view(), name='edit_finding'),
    # Reports
    path('report/create/', ReportCreateView.as_view(), name="create_report"),
    path('reports/', ReportListView.as_view(), name="report_list"),
    path('report/edit/<int:pk>/', ReportEditView.as_view(), name="edit_report"),
    path('reports/generate/', GenerateReportView.as_view(), name='generate_report'),
    # ClientContact URLs
    path('clientcontacts/', ClientContactListView.as_view(), name="clientcontact_list"),
    path('clientcontact/edit/<int:pk>/', ClientContactUpdateView.as_view(), name="edit_clientcontact"),
    path('clientcontact/create/', ClientContactCreateView.as_view(), name="create_clientcontact"),
    # RTContact URLs
    path('rtcontacts/', RTContactListView.as_view(), name="rtcontact_list"),
    path('rtcontact/edit/<int:pk>/', RTContactUpdateView.as_view(), name="edit_rtcontact"),
    path('rtcontact/create/', RTContactCreateView.as_view(), name="create_rtcontact"),
    # ScoreOverride URLs
    path('scoreoverrides/', ScoreOverrideListView.as_view(), name="scoreoverride_list"),
    path('scoreoverride/edit/<int:pk>/', ScoreOverrideUpdateView.as_view(), name="edit_scoreoverride"),
    path('scoreoverride/create/', ScoreOverrideCreateView.as_view(), name="create_scoreoverride"),
    # Strength URLs
    path('strengths/', StrengthListView.as_view(), name="strength_list"),
    path('strength/edit/<int:pk>/', StrengthUpdateView.as_view(), name="edit_strength"),
    path('strength/create/', StrengthCreateView.as_view(), name="create_strength"),
    # Improvement URLs
    path('improvements/', ImprovementListView.as_view(), name="improvement_list"),
    path('improvement/edit/<int:pk>/', ImprovementUpdateView.as_view(), name="edit_improvement"),
    path('improvement/create/', ImprovementCreateView.as_view(), name="create_improvement"),
    # SolutionOverride URLs
    path('solutionoverrides/', SolutionOverrideListView.as_view(), name="solutionoverride_list"),
    path('solutionoverride/edit/<int:pk>/', SolutionOverrideUpdateView.as_view(), name="edit_solutionoverride"),
    path('solutionoverride/create/', SolutionOverrideCreateView.as_view(), name="create_solutionoverride"),
]
urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
