---
name: agile-product-owner
description: "Agile product ownership toolkit for Senior Product Owner including INVEST-compliant user story generation, sprint planning, backlog management, and velocity tracking. Use for story writing, sprint planning, stakeholder communication, and agile ceremonies."
---

# Agile Product Owner

Complete toolkit for Product Owners to excel at backlog management and sprint execution.

## Core Capabilities

- INVEST-compliant user story generation with acceptance criteria
- Sprint capacity planning and backlog prioritization
- Velocity tracking, metrics, and stakeholder communication

## Workflow

### 1. Story Generation

Accept an epic or feature description, then:

1. Break the epic into INVEST-compliant user stories
2. Write each story in standard format with acceptance criteria (Given/When/Then)
3. Estimate story points using team baseline
4. Assign priority based on value and dependencies

### 2. Sprint Planning

1. Gather team capacity (available points for the sprint)
2. Prioritize the backlog by business value and effort
3. Select stories that fit within capacity
4. Validate the sprint goal is coherent and achievable

### 3. Backlog Refinement

1. Review upcoming stories for clarity and readiness
2. Split stories larger than 8 points into smaller deliverables
3. Update priorities based on stakeholder feedback
4. Remove stale or obsoleted items

## Example: Epic to User Story

**Input epic:** "Users need to reset their passwords"

**Output story:**

```
Title: Password Reset via Email
As a registered user,
I want to reset my password via email,
So that I can regain access to my account when I forget my credentials.

Acceptance Criteria:
- Given I am on the login page,
  When I click "Forgot Password" and enter my registered email,
  Then I receive a password reset link within 2 minutes.
- Given I have received a reset link,
  When I click the link and enter a new valid password,
  Then my password is updated and I can log in with it.
- Given a reset link has been used or is older than 24 hours,
  When I click the link,
  Then I see an error message asking me to request a new link.

Story Points: 3
Priority: High
Labels: authentication, security
```

## Scripts

Generate stories and plan sprints using the included helper:

```bash
# Generate stories from an epic
python scripts/user_story_generator.py

# Plan a sprint with team capacity of 40 points
python scripts/user_story_generator.py sprint 40
```

Sample sprint plan output:

```
Sprint 12 — Goal: "Improve account security"
Capacity: 40 pts | Committed: 37 pts | Buffer: 3 pts

Selected Stories:
  [HIGH]  Password Reset via Email          3 pts
  [HIGH]  Two-Factor Authentication Setup   8 pts
  [MED]   Session Timeout Configuration     5 pts
  ...
```

## References

- `references/story-templates.md` — reusable story templates by domain
- `references/sprint-planning.md` — detailed capacity planning guide
- `references/invest-checklist.md` — INVEST criteria validation checklist
