# ICE QA Team Structure

## Team Leadership

**QA Lead:** Sarah Chen
- Email: sarah.chen@ice-internal.com
- Slack: @sarah.chen
- Office: Room 3-315 (Atlanta HQ)
- Responsible for: Sprint planning, test strategy, team mentorship, stakeholder reporting
- Best for: Questions about test priorities, sprint scope, technical decisions, code review escalations

**QA Manager:** David Kim
- Email: david.kim@ice-internal.com
- Office: Room 3-320 (Atlanta HQ)
- Oversees: All QA sub-teams, budget, hiring, cross-team coordination
- Best for: Career development discussions, team concerns, resource allocation, cross-team issues

## Team Composition

### Manual QA Engineers (3 engineers)
- **Focus area:** Clearing and settlement workflow validation
- **Key responsibilities:**
  - Exploratory testing of new clearing features
  - Trade lifecycle validation across environments
  - User acceptance testing (UAT) support for STAGING releases
  - Test case documentation and maintenance in Confluence
- **Team members:** Priya Patel, James Okafor, Maria Santos
- **Slack channel:** #qa-manual

### Automation QA Engineers (4 engineers)
- **Focus area:** Playwright UI automation, API testing, performance validation
- **Key responsibilities:**
  - Building and maintaining the Playwright test suite
  - API contract testing with Pact
  - CI/CD pipeline test integration (GitHub Actions)
  - Test framework maintenance and tooling improvements
- **Team members:** Alex Rivera, Yuki Tanaka, Omar Hassan, Emily Park
- **Slack channel:** #qa-automation

### Performance QA Engineers (2 engineers)
- **Focus area:** Load testing, stress testing, matching engine performance
- **Key responsibilities:**
  - JMeter load test script development and execution
  - Matching engine throughput testing (target: 10,000 trades/second)
  - Performance regression detection
  - Capacity planning support for infrastructure team
- **Team members:** Raj Krishnamurthy, Tom Williams
- **Slack channel:** #qa-performance

## Sprint Cadence

- **Sprint duration:** 2 weeks
- **QA involvement:** From sprint planning through to release sign-off
- Sprint boundaries align with the QA environment refresh schedule
- **Sprint naming convention:** Q[Quarter]-S[Sprint Number] (e.g., Q1-S3 = Quarter 1, Sprint 3)

## Ceremonies

| Ceremony | Schedule | Duration | Location |
|----------|----------|----------|----------|
| Daily Standup | Mon–Fri, 9:30 AM EST | 15 minutes | #qa-standup Slack channel (async on Fridays) |
| Sprint Planning | Every other Monday, 10:00 AM | 1 hour | Conference Room "Thames" |
| Sprint Review/Demo | Every other Friday, 2:00 PM | 30 minutes | Conference Room "Hudson" |
| Retrospective | Every other Friday, 3:00 PM | 45 minutes | Conference Room "Hudson" |
| QA Sync (cross-team) | Wednesday, 11:00 AM | 30 minutes | Zoom (hybrid) |
| Bug Triage | Tuesday, 2:00 PM | 30 minutes | Conference Room "Thames" |

### What to Expect in Each Ceremony

- **Daily Standup:** Each person answers: What did you do yesterday? What are you doing today? Any blockers? Keep it under 2 minutes per person. On Fridays, post your update async in #qa-standup.
- **Sprint Planning:** QA Lead presents the test scope for the sprint. We estimate test effort, assign test cases, and identify automation candidates. New hires: just observe for the first 2 sprints.
- **Sprint Review/Demo:** Team demos completed work to stakeholders. If you automated something cool, this is the place to show it off.
- **Retrospective:** What went well? What didn't? What to improve? Honest feedback is expected and valued. Retro action items are tracked in Confluence.
- **QA Sync:** Cross-team coordination with Manual QA, Performance QA, and engineering. Good for understanding the bigger picture.
- **Bug Triage:** Review new bugs, assign severity, and prioritize for the current sprint. QA Lead facilitates.

## Onboarding Buddy System

- Every new QA hire is assigned an **onboarding buddy** for their first **4 weeks**
- Your buddy is your go-to person for questions about tools, processes, and team culture
- Buddy assignments are made by the QA Lead based on sub-team alignment
- **What your buddy does:**
  - Walks you through the codebase and test architecture
  - Pairs with you on your first 2-3 test cases
  - Introduces you to the team and key stakeholders
  - Reviews your first few PRs and provides constructive feedback
  - Answers "dumb questions" (there are none — ask everything!)
- **What your buddy does NOT do:**
  - They are not your manager — performance feedback comes from QA Lead and QA Manager
  - They don't assign you work — that comes from sprint planning
- After 4 weeks, the formal buddy period ends, but you can always reach out to anyone on the team

## New Hire Learning Path

### Weeks 1–2: Foundation
- Complete all compliance training
- Set up development environment and tools
- Read QA Automation Standards and Test Environment Guide
- Shadow standups and pair with your buddy
- Run existing tests locally and understand the test architecture

### Weeks 3–4: First Contributions
- Write your first test case with buddy guidance
- Get comfortable with the PR review process
- Start participating in standups with brief updates
- Begin reviewing team PRs (reading only — comments welcome)

### Weeks 5–8: Building Independence
- Write test cases independently
- Start reviewing and approving PRs
- Take on a small sprint task independently
- Understand the full CI/CD pipeline and how tests fit in

### Weeks 9–12: Full Contributor
- Be contributing to every sprint
- Understand the clearing domain well enough to write tests without heavy guidance
- Be comfortable with both UI (Playwright) and API (pytest/requests) testing
- Be able to triage and file bugs independently

## Career Ladder

| Level | Title | Typical Experience | Key Expectations |
|-------|-------|--------------------|------------------|
| IC1 | QA Engineer I | 0–2 years | Write tests with guidance, follow established patterns |
| IC2 | QA Engineer II | 2–4 years | Write tests independently, review PRs, mentor IC1s |
| IC3 | Senior QA Engineer | 4–7 years | Own test strategy for a feature area, lead technical decisions |
| IC4 | Staff QA Engineer | 7+ years | Cross-team technical leadership, architecture decisions |
| M1 | QA Lead | 5+ years | Sprint planning, team mentorship, stakeholder management |
| M2 | QA Manager | 7+ years | Multi-team management, hiring, budget, process design |

- Promotions are discussed during the **end-of-year performance review cycle** (December)
- There is no minimum time-in-level requirement — promotions are based on demonstrated impact
- Both IC (individual contributor) and management tracks are available

## Cross-Training Rotation

- After 6 months on the team, QA engineers may request a **2-week rotation** with another QA sub-team
- Rotations are optional and must be scheduled around sprint commitments
- Available rotations:
  - **Manual QA → Automation:** Learn Playwright, contribute to the automation suite
  - **Automation → Performance:** Learn JMeter, run load tests on the matching engine
  - **Automation → Manual:** Understand exploratory testing approaches, improve test design skills
- Request a rotation through the QA Lead. Rotations are subject to team capacity.

## Communication Channels

| Channel | Purpose |
|---------|---------|
| #qa-team | General QA team discussions |
| #qa-automation | Automation framework, Playwright, CI/CD topics |
| #qa-manual | Manual testing discussions, exploratory session results |
| #qa-performance | Load testing, JMeter, performance benchmarks |
| #qa-regression-results | Nightly regression suite results (automated) |
| #qa-environments | Environment status, refresh schedules, outages |
| #qa-standup | Async standup updates (used for Friday async standups) |
| #qa-new-hires | Onboarding questions, new hire introductions (first 90 days) |

## Reporting & Metrics

The QA team tracks the following metrics weekly:
- **Test coverage:** Percentage of requirements covered by automated tests (target: 80%+)
- **Defect density:** Bugs found per feature/module
- **Automation rate:** Percentage of test cases automated vs. manual (target: 70%+)
- **Regression pass rate:** Nightly regression suite success percentage (target: 98%+)
- **Mean time to detect (MTTD):** Average time from defect introduction to detection
- **Flaky test rate:** Percentage of tests that produce inconsistent results (target: <2%)

Metrics are reviewed in the Wednesday **QA Sync** and displayed on the QA dashboard in Grafana.
