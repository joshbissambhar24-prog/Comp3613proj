# Sprint 2 testing report — StackSync (UWI Connect)

## Scope and provenance

- Prior developer local test screenshot: **22 passing automated tests** (before adding `test_sprint2_workflows.py`).
- Prior selected-feature coverage: **75%** across seven named service modules.
- Prior overall application coverage: **27%** across the full `app` package. **These are not interchangeable.**
- API walkthrough screenshots supplied on 23 November 2026: listing #3 and campaign #1; verified recipient ID 2 had listing and campaign notifications; unverified ID 3 had an empty inbox.
- **New integration suite: not yet executed on the user's machine as of this package. Do not claim that the new tests passed until verified.**

## Exact new test commands (safe isolated database)

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/run_sprint2_tests.py tests/test_sprint2_workflows.py -v
.\.venv\Scripts\python.exe scripts/run_sprint2_tests.py tests -v
.\.venv\Scripts\python.exe scripts/run_sprint2_tests.py tests --cov=app --cov-report=term-missing --cov-report=html
```

The safe runner is necessary for a full-suite run because the inherited `tests/test_scenario.py` invokes `seed(reset=True)` and resets its configured database. Do **not** run the entire suite against your real data or production DB.

## Feature-specific coverage command

```powershell
.\.venv\Scripts\python.exe scripts/run_sprint2_tests.py tests --cov=app.services.event_bus --cov=app.services.notifications --cov=app.services.notification_observer --cov=app.services.retry_observer --cov=app.services.recipient_policy --cov=app.services.boards --cov=app.services.campaigns --cov-report=term-missing
```

## Task #18 integration checks

| Check | Test function | What it validates |
|---|---|---|
| Job + event listing workflow | `test_listing_approval_creates_verified_only_notifications` | Pending → published; Observer → inbox; eligible-only, reject double publish |
| Campaign workflow | `test_campaign_send_creates_verified_only_notifications` | Draft → sent; in-app persistence; verified-only; no second send |
| Rejection handling | `test_rejected_listing_is_not_published_or_notified` | Rejected listing stays hidden and dispatches nothing |
| Role restrictions | `test_unverified_cannot_submit_and_alumnus_cannot_publish` | Unverified submit rejected and alumni cannot publish |
| Verify eligibility | `test_verification_changes_eligibility_for_future_campaign` | Documents current **demo-only** email verification behavior |
| Failure path | `test_campaign_observer_failure_is_reported` | Failed persistence recorded; three retry attempts; no false-success inbox |
| Campaign permissions | `test_non_admin_cannot_manage_campaigns` | Non-admin campaign create/send blocked |
| Idempotence | `test_shared_observer_is_idempotent_for_same_source_event` | Repeat event does not create duplicate records |

### Fill in after running (do not fabricate results)

- Commit SHA: ___________________
- Tester and run date: ___________________
- Python version: ___________________
- Targeted integration suite: ____ passed / ____ failed / ____ errors
- Complete suite: ____ passed / ____ failed / ____ xfailed
- Selected-feature coverage: ____%  |  Whole-app coverage: ____%
- Peer reviewer, PR link, and approval date: ___________________
- Screenshot/test log attached to Trello #18: Yes / No

## Interpretation and limits

The developer checks validate the application **as implemented**, including the demo verification stub and failure-count behavior. They do not prove email ownership, reject reasons, durable per-user delivery statuses, or cross-process/concurrent deduplication. See `SPRINT2_KNOWN_GAPS.md`.
