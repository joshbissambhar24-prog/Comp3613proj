# Sprint 2 task and review evidence — StackSync

**Current board:** https://trello.com/b/3VdG9gap  
**Public code:** https://github.com/joshbissambhar24-prog/Comp3613proj  
**Team-supplied invite:** https://trello.com/invite/b/6af954686e6fbf4892cbf92c/ATTI52919d95dceaff9e761c019fae4193a9C49055A5/  

**Snapshot date:** 24 November 2026. This table records current board statuses and evidence; a Completed status is not proof that all checklist items or peer review are satisfied.

### Sprint 1 task register

| Task | Description | Assigned owner | Status | Trello |
|---|---|---|---|---|
| #1 | Set up GitHub repository | Josh | Completed (board status) | [Card](https://trello.com/c/vwgaQAKy) |
| #2 | Configure Trello board | Kyle | Completed (board status) | [Card](https://trello.com/c/jiz1wokC) |
| #3 | Conduct stakeholder interviews | Josh | Completed (board status) | [Card](https://trello.com/c/7Wo6w03a) |
| #4 | Document FR/NFR requirements | Kyle | Completed (board status) | [Card](https://trello.com/c/cu5iOfBp) |
| #5 | Create use-case diagram | Stephen | Completed (board status) | [Card](https://trello.com/c/VOqb2pqz) |
| #6 | Inspect inherited defects | Stephen | Completed (board status) | [Card](https://trello.com/c/ijgmLliB) |
| #7 | Observer class diagram redesign | Josh | Completed (board status) | [Card](https://trello.com/c/hveXjJDo) |
| #8 | Pattern justification | Kyle | Completed (board status) | [Card](https://trello.com/c/S1fCOoXF) |
| #9 | Sprint 1 report draft | Stephen | Completed (board status) | [Card](https://trello.com/c/GJBptQIo) |
| #10 | Sprint 1 review & retrospective | Stephen | Completed (board status) | [Card](https://trello.com/c/KpYko08W) |

### Sprint 2 task register

| Task | Description | Assigned owner | Status | Trello |
|---|---|---|---|---|
| #11 | Observer subject and event bus | Josh | Completed (board status) | [Card](https://trello.com/c/jWbRqppc) |
| #12 | In-app notification observer | Kyle | Completed (board status) | [Card](https://trello.com/c/4BWa9KK1) |
| #13 | Listing publication integration | Stephen | Completed (board status) | [Card](https://trello.com/c/tO0261M9) |
| #14 | Campaign notification integration | Kyle | Completed (board status) | [Card](https://trello.com/c/nQvkjqJ0) |
| #15 | Verified-recipient filtering | Stephen | Completed (board status) | [Card](https://trello.com/c/qFtkpEhv) |
| #16 | Bounded retries and failure handling | Josh (originally Stephen) | Completed (board status) | [Card](https://trello.com/c/uJNGotXM) |
| #17 | Observer pattern unit tests | Josh | Completed (board status) | [Card](https://trello.com/c/BGlmQmRc) |
| #18 | Automated listing and campaign integration tests | Kyle (planned) | Review — incomplete | [Card](https://trello.com/c/T6fLIRTg) |
| #19 | Run tests and record evidence | Josh | Completed (board status) | [Card](https://trello.com/c/llPEEKko) |
| #20 | Sprint 2 review / retrospective | Kyle | Completed (board status) | [Card](https://trello.com/c/iG9gZC6N) |

### Sprint 3 task register

| Task | Description | Assigned owner | Status | Trello |
|---|---|---|---|---|
| #21 | Prepare production deployment | Kyle | Planned / Backlog | [Card](https://trello.com/c/YNwW9hZf) |
| #22 | Deploy UWI Connect | Josh | Planned / Backlog | [Card](https://trello.com/c/TzL4x2N3) |
| #23 | Verify deployed special feature | Stephen | Planned / Backlog | [Card](https://trello.com/c/RBCMFHL9) |
| #24 | Final presentation slides | Kyle | Planned / Backlog | [Card](https://trello.com/c/G2KuoKKo) |
| #25 | Record Observer demonstration video | Josh | Planned / Backlog | [Card](https://trello.com/c/em0W4StZ) |
| #26 | Update final report | Stephen | Planned / Backlog | [Card](https://trello.com/c/oaqOIIYd) |
| #27 | Prepare individual technical exit interviews | Kyle | Planned / Backlog | [Card](https://trello.com/c/agB6zTLY) |
| #28 | Audit GitHub/Trello contribution evidence | Josh | Planned / Backlog | [Card](https://trello.com/c/iAh9kMe9) |
| #29 | Sprint 3 review / retrospective | Stephen | Planned / Backlog | [Card](https://trello.com/c/BlGLF6WD) |
| #30 | Compile and submit final deliverables | Josh | Planned / Backlog | [Card](https://trello.com/c/Oq2An6Rk) |

## Sprint 2 evidence references

- **PR #1:** [Observer subject and events](https://github.com/joshbissambhar24-prog/Comp3613proj/pull/1)
- **PR #2:** [Listing/campaign Observer integration](https://github.com/joshbissambhar24-prog/Comp3613proj/pull/2)
- **PR #3:** [Retry and failure handling](https://github.com/joshbissambhar24-prog/Comp3613proj/pull/3)
- **Kyle code:** [In-app observer and campaigns commit](https://github.com/joshbissambhar24-prog/Comp3613proj/commit/2edfe8e0592596628ab3a09c33370bafe91a1849)
- **Stephen code:** [Approval and verified-recipient policy commit](https://github.com/joshbissambhar24-prog/Comp3613proj/commit/a6f0ae4eecc0e9a53bc770d707980ba08381d274)
- **Tests:** [Repository test directory](https://github.com/joshbissambhar24-prog/Comp3613proj/tree/main/tests)
- **Developer Swagger walkthrough:** listing #3 published; campaign #1 sent; verified user #2 has both notifications; unverified ID #3 receives none (see user's report/UAT screenshot appendix).

## Sprint 2 review / retrospective

The team implemented shared Observer dispatch and persistence, bounded retries and verified-recipient filtering. Known gaps include durable retry state, secure email verification, rejection reasons, and full automation of listing/campaign workflow tests. **Task #18 was returned to Review** when the missing end-to-end automated tests were identified. No fabricated peer approval is recorded. Improvements for Sprint 3: keep PRs scoped, assign actual Trello members, document known defects and tests with traceable outputs, and obtain genuine reviews.

## Sprint 3 planning

Tasks #21–#30 remain Planned / Backlog. Prioritize reliable automated tests and UAT, deployment and verification, presentation video/slides, final report, contribution audit and exit interviews. Do not treat plans as completed work.
