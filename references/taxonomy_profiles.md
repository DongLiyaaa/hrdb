# Taxonomy Profiles

Use generalized labels by default. Switch to a domain-specific profile only when the user's dataset clearly belongs to that domain.

## General profile

- `domain_label`: operations, sales, support, product, engineering, finance, hr, procurement, marketing, cross-functional, other
- `topic_label`: planning, reporting, execution, escalation, handoff, tooling, permissions, customer issue, delivery, documentation, ai-usage, other
- `issue_label`: unclear request, missing data, tool failure, permissions, execution gap, quality check, coordination gap, repeated task, no-clear-issue
- `task_maturity_label`: ambiguous, clear, structured, data-driven, actionable, follow-up
- `message_value_label`: question, answer, decision, action-item, risk, summary, signal, noise
- `tone_label`: normal, urgent, blocking, corrective, negative, appreciative

## E-commerce example profile

Use only when the team obviously works in e-commerce or marketplace operations.

- `domain_label`: advertising, listing, inventory, pricing, design, support, logistics, finance
- `topic_label`: campaign-analysis, listing-optimization, keyword-research, competitor-review, replenishment, margin, review-risk, sop-buildout
- `issue_label`: tool-usage, data-read, prompt-quality, business-understanding, execution-gap, review-loop, coordination-gap, verification-gap

## Guidance

- Do not force the e-commerce profile onto unrelated companies.
- If the domain is mixed, start with the general profile and add a narrow custom vocabulary in `analysis_json`.
- When confidence is low, store a coarse label and explain the ambiguity in the report.
