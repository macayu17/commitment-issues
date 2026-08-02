---
description: Prepare a complete, immutable review package for the current local contribution.
argument-hint: '[issue|pr]'
disable-model-invocation: true
---

Use $commitment-issues with the raw `$ARGUMENTS` unchanged to produce its complete review package, including scope, diff summary, tests, risks, exact head SHA, proposed commit and pull-request text, and a SHA-256 fingerprint of `git diff`. Do not modify local or remote state.
