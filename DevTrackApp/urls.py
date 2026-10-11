from django.urls import path

from .views import (
    create_issues,
    get_all_reporters,
    get_issue_by_id,
    get_issues_by_reporter_id,
    get_issues_by_status,
    get_reporter_by_id,
    get_reporter_by_name,
    get_reporters_by_id,
)


urlpatterns = [
   path("api/reporters/", get_all_reporters, name='get_all_reporters'),
   path("api/reporters/limit/", get_reporters_by_id, name='get_reporters_by_id'),
   path("api/reporters/id/<int:reporter_id>/", get_reporter_by_id, name='get_reporter_by_id'),
   path("api/reporters/<str:name>/", get_reporter_by_name, name='get_reporter_by_name'),
   path("api/issues/", create_issues, name='create_issues'),
   path("api/issues/id/<int:issue_id>/", get_issue_by_id, name='get_issue_by_id'),
   path("api/issues/reporter/<int:reporter_id>/", get_issues_by_reporter_id, name='get_issues_by_reporter_id'),
   path("api/issues/<str:status>/", get_issues_by_status, name='get_issues_by_status'),
   path("api/issues/status/<str:status>/", get_issues_by_status, name='get_issues_by_status'),
]