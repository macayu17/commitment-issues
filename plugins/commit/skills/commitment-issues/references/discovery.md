# Discovery and issue vetting

Use live, read-only evidence. Bare `shop` searches repositories from the authenticated user's authored pull-request history, a 7-day creation window, and at most three candidates. An explicit owner or repository replaces that universe; `--since` and `--limit` override the numeric defaults.

## Candidate checks

1. Confirm the issue is open and recent enough for the requested window. Older issues require fresh maintainer activity or explicit user interest.
2. Require the issue author's association to be `OWNER`, `MEMBER`, `COLLABORATOR`, or `CONTRIBUTOR`; never equate association with assignment.
3. Reject assigned issues and issues with any comment outside `OWNER`, `MEMBER`, or `COLLABORATOR`. Inspect remaining maintainer comments for claims or reservations.
4. Search issue titles and bodies for duplicates, then inspect likely duplicate discussions and their resolution.
5. Reject any linked, closing, or cross-referenced pull request in the complete timeline, including closed, draft, and fork work.
6. Search open pull-request titles and bodies for the issue number, URL, distinctive error text, and feature wording. A missing formal link is not proof of no competing work.
7. Check labels, reproduction quality, requested scope, repository eligibility rules, and whether maintainers have supplied a clear direction.
8. Report evidence gaps. `scripts/vet_issue.py` provides deterministic collection and classification, but incomplete API results or semantic duplicates still require manual inspection.

Reject candidates with any pull-request evidence, non-maintainer comments, a clear claim, closed or superseded scope, prohibited contribution mode, or work too ambiguous to implement safely. Label uncertain ownership, design, or reproduction as needing review rather than available.

## Recheck boundary

Re-run the relevant issue, timeline, claim, and pull-request checks immediately before implementation. Discovery results are a shortlist, not a reservation. Recheck again before any public action because assignments, competing work, and target branches can change.

Return compact evidence for every candidate: repository and issue, freshness, author association, claim/assignee state, duplicate result, timeline and pull-request-body result, fit, blockers, and direct source links when available.
