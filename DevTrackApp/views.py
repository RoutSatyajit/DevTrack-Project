import json
from datetime import datetime
from pathlib import Path

from rest_framework.decorators import api_view
from rest_framework.response import Response

REPORTERS_FILE = Path(__file__).resolve().parent / "files" / "reporters.json"
ISSUES_FILE = Path(__file__).resolve().parent / "files" / "issues.json"


@api_view(['GET', 'POST'])
def get_all_reporters(request):
    with REPORTERS_FILE.open(encoding='utf-8') as f:
        reporters = json.load(f)

    if request.method == 'POST':
        reporter = request.data
        if not isinstance(reporter, dict) or not reporter:
            return Response({'error': 'A reporter JSON object is required.'}, status=400)
        reporter_id = reporter.get('id')
        if reporter_id is not None and str(reporter_id).strip():
            normalized_id = str(reporter_id).strip()
            if any(
                existing.get('id') is not None
                and str(existing['id']).strip() == normalized_id
                for existing in reporters
            ):
                return Response({'error': 'A reporter with this ID already exists.'}, status=409)
        email = reporter.get('email')
        if isinstance(email, str) and email.strip():
            normalized_email = email.strip().casefold()
            if any(
                isinstance(existing.get('email'), str)
                and existing['email'].strip().casefold() == normalized_email
                for existing in reporters
            ):
                return Response({'error': 'A reporter with this email already exists.'}, status=409)
        reporters.append(reporter)
        with REPORTERS_FILE.open('w', encoding='utf-8') as f:
            json.dump(reporters, f, indent=4)
        return Response(reporter, status=201)

    reporter_id = request.query_params.get('id')
    if reporter_id is not None:
        try:
            reporter_id = int(reporter_id)
        except ValueError:
            return Response({'error': 'Reporter not found'}, status=404)
        reporter = next((r for r in reporters if r.get('id') == reporter_id), None)
        if reporter is None:
            return Response({'error': 'Reporter not found'}, status=404)
        return Response(reporter)

    return Response(reporters)


@api_view(['GET'])
def get_reporter_by_name(request, name):
    with REPORTERS_FILE.open(encoding='utf-8') as f:
        reporters = json.load(f)
    reporter = next((r for r in reporters if r['name'] == name), None)
    if reporter:
        return Response(reporter)
    else:
        return Response({'error': 'Reporter not found'}, status=404)


@api_view(['GET'])
def get_reporter_by_id(request, reporter_id):
    with REPORTERS_FILE.open(encoding='utf-8') as f:
        reporters = json.load(f)
    reporter = next((r for r in reporters if r.get('id') == reporter_id), None)
    if reporter:
        return Response(reporter)
    return Response({'error': 'Reporter not found'}, status=404)


@api_view(['GET'])
def get_reporters_by_id(request):
    count = request.query_params.get('id')
    try:
        count = int(count)
    except (TypeError, ValueError):
        return Response({'error': 'The id query parameter must be a positive integer.'}, status=400)

    if count < 1:
        return Response({'error': 'The id query parameter must be a positive integer.'}, status=400)

    with REPORTERS_FILE.open(encoding='utf-8') as f:
        reporters = json.load(f)
    return Response(reporters[:count])

@api_view(['GET', 'POST'])
def create_issues(request):
    with ISSUES_FILE.open(encoding='utf-8') as f:
        issues = json.load(f)
    if isinstance(issues, dict):
        issues = [issues]

    if request.method == 'POST':
        issue = request.data
        if not isinstance(issue, dict) or not issue:
            return Response({'error': 'An issue JSON object is required.'}, status=400)

        for field in ('title', 'description'):
            if not isinstance(issue.get(field), str) or not issue[field].strip():
                return Response(
                    {'error': f'A non-empty {field} is required.'},
                    status=400,
                )
        if issue.get('status') not in {'open', 'in_progress', 'resolved', 'closed'}:
            return Response(
                {'error': 'Invalid status. Allowed values: open, in_progress, resolved, closed'},
                status=400,
            )
        if issue.get('priority') not in {'low', 'medium', 'high', 'critical'}:
            return Response(
                {'error': 'Invalid priority. Allowed values: low, medium, high, critical.'},
                status=400,
            )

        reporter_id = issue.get('reporter_id')
        try:
            reporter_id = int(reporter_id)
        except (TypeError, ValueError):
            return Response(
                {'error': 'A valid reporter_id is required to create an issue.'},
                status=400,
            )

        with REPORTERS_FILE.open(encoding='utf-8') as f:
            reporters = json.load(f)
        if not isinstance(reporters, list) or not any(
            reporter.get('id') == reporter_id
            for reporter in reporters
            if isinstance(reporter, dict)
        ):
            return Response(
                {'error': f'Reporter with id {reporter_id} not found.'},
                status=400,
            )

        existing_ids = [
            existing['id']
            for existing in issues
            if isinstance(existing, dict)
            and isinstance(existing.get('id'), int)
            and not isinstance(existing.get('id'), bool)
        ]
        issue['id'] = max(existing_ids, default=0) + 1
        issue['reporter_id'] = reporter_id
        issue.setdefault('created_at', str(datetime.now()))
        issues.append(issue)
        with ISSUES_FILE.open('w', encoding='utf-8') as f:
            json.dump(issues, f, indent=4)
        return Response(issue, status=201)

    issue_id = request.query_params.get('id')
    if issue_id is not None:
        try:
            issue_id = int(issue_id)
        except ValueError:
            return Response({'error': 'Issue not found'}, status=404)
        issue = next((item for item in issues if item.get('id') == issue_id), None)
        if issue is None:
            return Response({'error': 'Issue not found'}, status=404)
        return Response(issue)

    return Response(issues)
       
@api_view(['GET'])
def get_issues_by_reporter_id(request, reporter_id):
    with ISSUES_FILE.open(encoding='utf-8') as f:
        issues = json.load(f)
    if isinstance(issues, dict):
        issues = [issues]
    reporter_issues = [issue for issue in issues if issue.get('reporter_id') == reporter_id]
    return Response(reporter_issues)


@api_view(['GET'])
def get_issue_by_id(request, issue_id):
    with ISSUES_FILE.open(encoding='utf-8') as f:
        issues = json.load(f)
    if isinstance(issues, dict):
        issues = [issues]
    issue = next((issue for issue in issues if issue.get('id') == issue_id), None)
    if issue is None:
        return Response({'error': 'Issue not found'}, status=404)
    return Response(issue)

@api_view(['GET'])
def get_issues_by_status(request, status):
    with ISSUES_FILE.open(encoding='utf-8') as f:
        issues = json.load(f)
    status_issues = [issue for issue in issues if issue.get('status') == status]
    return Response(status_issues)