# ICE Deployment Pipeline

## Pipeline Overview

The ICE deployment pipeline follows a strict, gated process to ensure quality and stability:

```
Pull Request → Code Review → GitHub Actions CI → QA Sign-off → Staging Deploy → Prod Deploy
```

Each stage must pass before the next stage begins. There are no shortcuts or bypasses.

## Stage Details

### 1. Pull Request (PR)

- All code changes must go through a Pull Request in **GitHub Enterprise**
- PR must include:
  - Clear description of the change
  - Link to the Jira ticket (e.g., `ICE-QA-1234`)
  - Screenshots for any UI changes
  - Test evidence (new/updated test cases)
- Branch naming convention: `feature/ICE-QA-1234-short-description` or `bugfix/ICE-QA-5678-fix-description`

### 2. Code Review

- Minimum **2 approvals** required (1 from QA, 1 from Engineering)
- Reviewers check for:
  - Code quality and adherence to standards
  - Test coverage (new features must have tests)
  - Security considerations (no hardcoded credentials, no SQL injection vulnerabilities)
  - Performance implications
- Review SLA: Reviews should be completed within **24 hours**

### 3. GitHub Actions CI

The CI pipeline runs automatically on every PR push:

```yaml
Pipeline Steps:
  1. Lint (flake8, black)          ~2 min
  2. Unit Tests (pytest)           ~5 min
  3. Integration Tests (Playwright) ~15 min
  4. Security Scan (Snyk)          ~3 min
  5. Build Artifact                ~2 min
  6. Test Report (Allure)          ~1 min
```

- **All steps must pass** — any failure blocks the merge
- Test results and Allure reports are attached to the PR as comments
- Security vulnerabilities flagged by Snyk must be resolved before merge

### 4. QA Sign-off (QA Gate)

This is the QA team's critical checkpoint before any deployment:

**QA Gate Criteria:**
- All **P1 and P2 test cases** must pass (100% pass rate)
- **Zero open S1 or S2 bugs** related to the release
- Regression suite must have a **pass rate ≥ 98%**
- Performance benchmarks must not degrade by more than **5%** from the baseline

**Sign-off Process:**
1. QA Lead reviews the test results dashboard
2. QA Lead verifies all gate criteria are met
3. QA Lead approves the release in Jira (transition ticket to "QA Approved")
4. Sign-off is recorded with timestamp and approver name

### 5. Staging Deployment

- Deployment to STAGING is automated via **Argo CD**
- After deployment, a **smoke test suite** runs automatically (10 critical path tests)
- QA team performs a quick **sanity check** on STAGING (30-minute window)
- Stakeholders may perform UAT on STAGING before production release
- STAGING environment must be stable for at least **2 hours** before proceeding to PROD

### 6. Production Deployment

- Prod deployments occur during the **deployment window: Tuesday and Thursday, 6:00 AM – 8:00 AM EST**
- Deployments outside the window require VP approval and an on-call engineer
- Post-deployment:
  - Automated smoke tests run against PROD
  - QA monitors the #alerts-prod Slack channel for 1 hour
  - Grafana dashboards are checked for anomalies (latency, error rates, throughput)

## Rollback Procedure

If a production deployment causes issues:

1. **Detection**: Automated alerts or QA/engineering observation
2. **Decision**: Engineering Lead or QA Lead calls for rollback
3. **Execution**: Rollback is automated via **Argo CD** — reverts to the previous stable version
4. **Verification**: QA runs the smoke test suite against the rolled-back version
5. **Post-mortem**: A post-mortem document is created within 24 hours, reviewed in the next team sync

### Rollback Triggers (automatic)
- Error rate exceeds **1%** for more than 5 minutes
- P95 latency exceeds **500ms** for more than 5 minutes
- Any S1 bug reported within 1 hour of deployment

## Hotfix Process

For critical production issues requiring immediate fix:

1. Branch from `main`: `hotfix/ICE-QA-XXXX-description`
2. Fix, test locally, and push
3. Expedited code review (1 approval from Engineering Lead)
4. CI pipeline runs (all steps must still pass)
5. QA Lead performs abbreviated sign-off (critical path tests only)
6. Deploy directly to STAGING → PROD (skip normal deployment window)
7. Full regression runs overnight to confirm no side effects
