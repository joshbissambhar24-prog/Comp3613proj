# StackSync — Sprint 2 GitHub integration package

This source tree includes the **current GitHub main branch** (verified against tree SHA `957843511064dc61e0992088179391b98d04d8bf`) plus the new Sprint 2 test and evidence files.

## What's new

- `tests/test_sprint2_workflows.py`: 9 API/Observer integration test cases; not yet run in the student's environment.
- `scripts/run_sprint2_tests.py`: runs existing and new tests with an isolated temporary SQLite database.
- `requirements-dev.txt`: development coverage dependency.
- `docs/SPRINT2_TESTING.md`, `docs/SPRINT2_UAT.md`, `docs/SPRINT2_KNOWN_GAPS.md`, `docs/SPRINT2_TASK_EVIDENCE.md` and review template.
- `docs/diagrams/`: updated editable diagrams and PNG/SVG views.

Run `PUSH_SPRINT2.ps1` from the *top-level extracted ZIP folder* to apply the new files to a proper clone, run tests and push a new branch. Do not simply upload the ZIP file as a GitHub repository file.

## Before marking Trello #18 complete

Run the 9 new tests and the whole suite, retain real output, create PR, obtain actual reviewer feedback. Unresolved capabilities such as rejection reason/email verification should remain documented as gaps.
