# Discovery and issue vetting

Use live, read-only evidence. Default `shop` to the current repository or the repository named by the active program rules, a 30-day freshness window, and at most three candidates.

## Candidate checks

1. Confirm the issue is open and recent enough for the requested window. Older issues require fresh maintainer activity or explicit user interest.
2. Inspect author association. Prefer issues opened or clearly endorsed by owners, members, or collaborators; never equate association with assignment.
3. Check assignees, explicit claims, maintainer reservations, and contributor comments that indicate work is underway.
4. Search issue titles and bodies for duplicates, then inspect likely duplicate discussions and their resolution.
5. Inspect the complete issue timeline for linked, closing, and cross-referenced pull requests, including drafts and work in forks.
6. Search open pull-request titles and bodies for the issue number, URL, distinctive error text, and feature wording. A missing formal link is not proof of no competing work.
7. Check labels, reproduction quality, requested scope, repository eligibility rules, and whether maintainers have supplied a clear direction.
8. Report evidence gaps. `scripts/vet_issue.py` provides deterministic collection and classification, but incomplete API results or semantic duplicates still require manual inspection.

Reject candidates with active competing implementation, a clear claim, closed or superseded scope, prohibited contribution mode, or work too ambiguous to implement safely. Label uncertain ownership, design, or reproduction as needing review rather than available.

## Recheck boundary

Re-run the relevant issue, timeline, claim, and pull-request checks immediately before implementation. Discovery results are a shortlist, not a reservation. Recheck again before any public action because assignments, competing work, and target branches can change.

Return compact evidence for every candidate: repository and issue, freshness, author association, claim/assignee state, duplicate result, timeline and pull-request-body result, fit, blockers, and direct source links when available.
