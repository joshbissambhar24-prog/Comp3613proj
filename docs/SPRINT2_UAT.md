# UWI Connect — Sprint 2 API acceptance record (developer-observed)

*Use with the professor's UAT table template. This does not replace independently conducted user acceptance testing.*

**Date observed:** 23 Nov 2026  
**Environment:** local Swagger `/docs` with demo seeded accounts  
**Status source:** screenshots from the actual API walkthrough  
**Stakeholder sign-off:** NOT PROVIDED — leave signature blank in the PDF.

| ID | Test case | Preconditions and steps | Expected | Observed | Status |
|---|---|---|---|---|---|
| UAT-01 | Verified alumni login | POST `/api/auth/login` with verified alumni credentials | 200 and user ID 2 | 200, ID 2 | Pass (developer API) |
| UAT-02 | Admin login | POST login with seeded admin | 200, admin ID 1 | 200, ID 1 | Pass (developer API) |
| UAT-03 | Job submission | POST `/api/boards/listings` as ID 2 | Listing created `pending` | Listing #3 pending | Pass (developer API) |
| UAT-04 | Publish listing | POST `/api/admin/listings/3/publish` as ID 1 | Listing becomes published, dispatch succeeds | `published`, zero reported notification failures | Pass (developer API) |
| UAT-05 | Verified recipient receives job | GET `/api/notifications` as ID 2 | `listing.published` in inbox | Event present, listing #3 | Pass (developer API) |
| UAT-06 | Unverified recipient excluded | GET inbox as ID 3 | No listing notification | `notifications: []` | Pass (developer API) |
| UAT-07 | Create campaign | POST `/api/admin/campaigns` as ID 1 | Draft created | Campaign #1 `draft` | Pass (developer API) |
| UAT-08 | Send campaign | POST `/api/admin/campaigns/1/send` as ID 1 | Campaign sent with no reported failures | `sent`, zero failures | Pass (developer API) |
| UAT-09 | Verified recipient receives campaign | GET inbox as ID 2 | `campaign.sent` present | Campaign #1 and listing #3 notifications | Pass (developer API) |
| UAT-10 | Unverified recipient excluded | GET inbox as ID 3 | No campaign notification | `notifications: []` | Pass (developer API) |

**Additional acceptance checks not yet observed:** rejection *reason* persistence and notification, end-user browser journey, durable delivery-status/retry visibility, and concurrency duplicate-prevention. These should be planned tests rather than signed-off passes.

**Caution:** campaign #1 used default `"string"` subject/body in the demonstration; this confirms event delivery but is not realistic campaign copy. The existing UAT PDF has a deliberately blank signature box.
