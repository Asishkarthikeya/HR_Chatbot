# ICE QA Team Structure

## Team Leadership

**QA Lead:** Sarah Chen
- Email: sarah.chen@ice-internal.com
- Slack: @sarah.chen
- Office: Room 3-315 (Atlanta HQ)
- Responsible for: Sprint planning, test strategy, team mentorship, stakeholder reporting

**QA Manager:** David Kim
- Email: david.kim@ice-internal.com
- Oversees: All QA sub-teams, budget, hiring, cross-team coordination

## Team Composition

### Manual QA Engineers (3 engineers)
- **Focus area:** Clearing and settlement workflow validation
- **Key responsibilities:**
  - Exploratory testing of new clearing features
  - Trade lifecycle validation across environments
  - User acceptance testing (UAT) support for STAGING releases
  - Test case documentation and maintenance in Confluence
- **Team members:** Priya Patel, James Okafor, Maria Santos

### Automation QA Engineers (4 engineers)
- **Focus area:** Playwright UI automation, API testing, performance validation
- **Key responsibilities:**
  - Building and maintaining the Playwright test suite
  - API contract testing with Pact
  - CI/CD pipeline test integration (GitHub Actions)
  - Test framework maintenance and tooling improvements
- **Team members:** Alex Rivera, Yuki Tanaka, Omar Hassan, Emily Park

### Performance QA Engineers (2 engineers)
- **Focus area:** Load testing, stress testing, matching engine performance
- **Key responsibilities:**
  - JMeter load test script development and execution
  - Matching engine throughput testing (target: 10,000 trades/second)
  - Performance regression detection
  - Capacity planning support for infrastructure team
- **Team members:** Raj Krishnamurthy, Tom Williams

## Sprint Cadence

- **Sprint duration:** 2 weeks
- **QA involvement:** From sprint planning through to release sign-off
- Sprint boundaries align with the QA environment refresh schedule

## Ceremonies

| Ceremony | Schedule | Duration | Location |
|----------|----------|----------|----------|
| Daily Standup | Mon–Fri, 9:30 AM EST | 15 minutes | #qa-standup Slack channel (async on Fridays) |
| Sprint Planning | Every other Monday, 10:00 AM | 1 hour | Conference Room "Thames" |
| Sprint Review/Demo | Every other Friday, 2:00 PM | 30 minutes | Conference Room "Hudson" |
| Retrospective | Every other Friday, 3:00 PM | 45 minutes | Conference Room "Hudson" |
| QA Sync (cross-team) | Wednesday, 11:00 AM | 30 minutes | Zoom (hybrid) |

## Onboarding Buddy System

- Every new QA hire is assigned an **onboarding buddy** for their first 4 weeks
- Your buddy is your go-to person for questions about tools, processes, and team culture
- Buddy assignments are made by the QA Lead based on sub-team alignment

## Communication Channels

| Channel | Purpose |
|---------|---------|
| #qa-team | General QA team discussions |
| #qa-automation | Automation framework, Playwright, CI/CD topics |
| #qa-regression-results | Nightly regression suite results (automated) |
| #qa-environments | Environment status, refresh schedules, outages |
| #qa-standup | Async standup updates |

## Reporting & Metrics

The QA team tracks the following metrics weekly:
- **Test coverage**: Percentage of requirements covered by automated tests
- **Defect density**: Bugs found per feature/module
- **Automation rate**: Percentage of test cases automated vs. manual
- **Regression pass rate**: Nightly regression suite success percentage
- **Mean time to detect (MTTD)**: Average time from defect introduction to detection
