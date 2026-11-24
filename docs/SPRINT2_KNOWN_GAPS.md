# Open product and verification gaps — 24 Nov 2026

The codebase was inspected against the public acceptance criteria and Task #18. These are **known limitations**, not claims of completed implementation.

1. **Automated workflow tests were not previously present.** The included `tests/test_sprint2_workflows.py` is a proposed addition; run it, attach the actual results, and obtain independent PR review before closing Task #18.
2. **Rejection reasons are not modeled.** `app/services/boards.py:reject_listing` changes `status` to rejected, but `Listing` has no reason field, and `/api/admin/listings/{id}/reject` does not accept one. Persisting a reason requires an API/model change and proper migration on existing databases; avoid adding a model column without migration.
3. **Email verification is only a demo stub.** `app/services/accounts.py:verify_email` marks accounts verified without token-based email ownership proof. `looks_like_uwi_email` is a loose substring check. This is unsuitable for real institutional verification.
4. **Public boards visibility gap.** The public GET `/api/boards` route does not authenticate the caller, despite `docs/ACCEPTANCE.md` saying unverified alumni cannot browse published boards.
5. **Delivery failure history is not durable.** `RetryObserver.history` is an in-memory bounded deque. Sending a campaign marks it sent even if a persistence observer fails; the response does report `notification_failures`.
6. **Duplicate prevention is sequential only.** The in-app observer reads before inserting, but there is no database-level unique constraint for `(user,event,source)` to handle concurrent requests safely.
7. **Email delivery / rejection notifications are not demonstrated.** The implemented special feature is persisted in-app notifications. Do not claim guaranteed email sends or rejection-reason notifications.
8. **Formal independent UAT sign-off and Trello member assignment** require actual human action. The report's signature field should remain blank until signed, and Trello review comments should accurately identify who reviewed.

## Suggested priorities

- **Before closing Sprint 2 Task #18:** Run the workflow tests, attach results and PR links, and complete actual peer review.
- **Sprint 3:** Rejection reason + migration, secure email verification, browse authorization, durable notification states and concurrency guarantees as time permits, deploy, and perform independent UAT.
