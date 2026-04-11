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
- Draft PRs are encouraged for early feedback — prefix with `[WIP]`

### 2. Code Review

- Minimum **2 approvals** required (1 from QA, 1 from Engineering)
- Reviewers check for:
  - Code quality and adherence to standards
  - Test coverage (new features must have tests)
  - Security considerations (no hardcoded credentials, no SQL injection vulnerabilities)
  - Performance implications
  - Backward compatibility
- Review SLA: Reviews should be completed within **24 hours**
- If a review is blocking your sprint work, escalate to the QA Lead or Engineering Lead

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
  Total:                           ~28 min
```

- **All steps must pass** — any failure blocks the merge
- Test results and Allure reports are attached to the PR as comments
- Security vulnerabilities flagged by Snyk must be resolved before merge (or explicitly waived by Engineering Lead)
- CI runs on dedicated GitHub Actions runners in the ICE private cloud

#### Lint Rules
- **flake8:** Enforces PEP 8 style guidelines (max line length: 120 characters)
- **black:** Enforces consistent formatting. Run `black .` before committing to auto-fix.
- **isort:** Import sorting. Run `isort .` to auto-fix import order.
- Fix all lint errors locally before pushing — don't rely on CI to catch them.

#### Security Scan Details
- **Snyk** scans for known vulnerabilities in Python dependencies
- Severity levels: Critical, High, Medium, Low
- **Critical and High** vulnerabilities block the merge
- Medium and Low are flagged as warnings — fix within the current sprint
- If a vulnerability has no available fix, request a waiver from the Engineering Lead via Jira

### 4. QA Sign-off (QA Gate)

This is the QA team's critical checkpoint before any deployment:

**QA Gate Criteria:**
- All **P1 and P2 test cases** must pass (100% pass rate)
- **Zero open S1 or S2 bugs** related to the release
- Regression suite must have a **pass rate ≥ 98%**
- Performance benchmarks must not degrade by more than **5%** from the baseline
- All new features have corresponding automated test coverage

**Sign-off Process:**
1. QA Lead reviews the test results dashboard in Grafana
2. QA Lead verifies all gate criteria are met
3. QA Lead approves the release in Jira (transition ticket to "QA Approved")
4. Sign-off is recorded with timestamp and approver name
5. If any criterion is not met, the release is blocked and sent back to engineering

### 5. Staging Deployment

- Deployment to STAGING is automated via **Argo CD**
- After deployment, a **smoke test suite** runs automatically (10 critical path tests)
- QA team performs a quick **sanity check** on STAGING (30-minute window)
- Stakeholders may perform UAT on STAGING before production release
- STAGING environment must be stable for at least **2 hours** before proceeding to PROD
- If smoke tests fail on STAGING, the deployment is automatically rolled back

### 6. Production Deployment

- Prod deployments occur during the **deployment window: Tuesday and Thursday, 6:00 AM – 8:00 AM EST**
- Deployments outside the window require VP approval and an on-call engineer
- Post-deployment:
  - Automated smoke tests run against PROD (10 critical path tests)
  - QA monitors the **#alerts-prod** Slack channel for 1 hour
  - Grafana dashboards are checked for anomalies (latency, error rates, throughput)
  - The deploying engineer stays on-call for **2 hours** after deployment

## Feature Flag Deployment

For high-risk features, ICE uses a **feature flag deployment** strategy:

1. Deploy the code to production **behind a feature flag** (disabled by default)
2. Enable for **internal users first** (ICE employees only)
3. Monitor for 24 hours with no issues
4. Enable for **10% of external users** (canary release)
5. Monitor for 24-48 hours
6. Enable for **100% of users** (full rollout)
7. Remove the feature flag in a follow-up PR (within 2 sprints)

Feature flags are managed through **LaunchDarkly**. QA is responsible for testing at each rollout stage.

## Canary Deployment

- Critical infrastructure changes use **canary deployment** via Argo CD
- Traffic is split: 5% to the new version, 95% to the current version
- Automated monitors watch for:
  - Error rate increase > 0.5%
  - Latency increase > 10%
  - Any 500-series errors
- If any monitor triggers, the canary is **automatically rolled back**
- Canary test duration: **30 minutes** minimum before full promotion

## Database Migration Testing

Database schema changes follow an additional testing process:

1. **Migration script review:** DBA reviews the migration SQL
2. **DEV test:** Run migration against a copy of the QA database
3. **Data integrity check:** Verify no data is lost or corrupted
4. **Rollback test:** Verify the rollback script works correctly
5. **Performance test:** Ensure the migration completes within the maintenance window
6. **QA approval:** QA Lead signs off on the migration testing

- All migrations use **Alembic** (Python) or **Flyway** (Java services)
- Migration scripts must be **idempotent** — safe to run multiple times
- Never run `DROP TABLE` or `DELETE` in production migrations — use soft deletes

## Rollback Procedure

If a production deployment causes issues:

1. **Detection**: Automated alerts or QA/engineering observation
2. **Decision**: Engineering Lead or QA Lead calls for rollback
3. **Execution**: Rollback is automated via **Argo CD** — reverts to the previous stable version
4. **Verification**: QA runs the smoke test suite against the rolled-back version
5. **Communication**: Notify stakeholders via #releases Slack channel
6. **Post-mortem**: A post-mortem document is created within 24 hours, reviewed in the next team sync

### Rollback Triggers (automatic)
- Error rate exceeds **1%** for more than 5 minutes
- P95 latency exceeds **500ms** for more than 5 minutes
- Any S1 bug reported within 1 hour of deployment
- Database connection failures

### Manual Rollback Command
```bash
# Argo CD rollback to previous revision
argocd app rollback clearing-platform --revision <previous-revision>

# Verify rollback
argocd app get clearing-platform
```

## Post-Deployment Monitoring Checklist

After every production deployment, QA monitors the following for **1 hour**:

- [ ] Smoke tests pass (automated)
- [ ] Error rate on Grafana dashboard is within normal range (<0.1%)
- [ ] P95 latency is within normal range (<200ms for API, <2s for UI)
- [ ] No S1 or S2 bugs reported by users or internal teams
- [ ] #alerts-prod Slack channel has no new alerts
- [ ] Key business metrics (trade volume, clearing throughput) are normal
- [ ] No customer complaints via support channels

## Hotfix Process

For critical production issues requiring immediate fix:

1. Branch from `main`: `hotfix/ICE-QA-XXXX-description`
2. Fix, test locally, and push
3. Expedited code review (**1 approval** from Engineering Lead — reduced from normal 2)
4. CI pipeline runs (all steps must still pass)
5. QA Lead performs abbreviated sign-off (critical path tests only)
6. Deploy directly to STAGING → PROD (skip normal deployment window)
7. Full regression runs overnight to confirm no side effects
8. Post-mortem within 24 hours

## Release Communication

- All releases are announced in the **#releases** Slack channel
- Announcement includes: version number, key changes, known issues, responsible engineer
- External-facing releases also notify the Product team for customer communication
- Release notes are maintained in Confluence under "Releases → [Quarter] → [Sprint]"
