# ICE Clearing Test Standards

## Trade Lifecycle Testing

All clearing system tests must validate the complete trade lifecycle:

```
Order Submission → Trade Matching → Clearing → Settlement
```

### Stage Definitions

1. **Order Submission**: Trade order is created with valid counterparty, instrument, and quantity
2. **Trade Matching**: Buy and sell orders are matched by the matching engine
3. **Clearing**: The clearinghouse validates margin, calculates obligations, and novates the trade
4. **Settlement**: Final transfer of securities and funds between counterparties

### Test Coverage Requirements
- Each lifecycle stage must have dedicated test cases
- End-to-end tests must cover the full lifecycle from order to settlement
- Negative test cases must cover rejection scenarios at each stage (e.g., insufficient margin, invalid instrument)
- At least **one happy path** and **three negative paths** per lifecycle stage

## Clearing-Specific Test Scenarios

### Margin Testing
- Verify initial margin calculation for each instrument type (equities, derivatives, commodities)
- Verify maintenance margin threshold triggers margin calls
- Test margin call notification delivery (email and Slack alert)
- Verify margin adjustment after partial settlement

### Novation Testing
- Verify the clearinghouse replaces counterparty risk (buyer → CCP ← seller)
- Test novation with mismatched trade details (should fail)
- Verify novation creates correct bilateral obligations
- Test novation cancellation within the allowed window

### Settlement Testing
- Verify T+1 settlement for equities (trade date + 1 business day)
- Verify T+0 settlement for cleared derivatives
- Test settlement failure handling (insufficient funds, failed delivery)
- Verify reconciliation between clearing records and settlement records
- Test partial settlement scenarios

### Market Data Testing
- Verify price feed updates are reflected in margin calculations within 5 seconds
- Test behavior when market data feed is delayed or unavailable
- Verify end-of-day price snapshots are used for daily mark-to-market
- Test handling of corporate actions (stock splits, dividends) in position calculations

## Teardown Rules

- **Every test must clean up after itself** using the `teardown()` hook or Playwright's built-in fixtures
- Mock trade data created during tests must be reverted after test completion
- Database state must be returned to its pre-test condition
- Use the `@pytest.fixture(autouse=True)` pattern for automatic cleanup:

```python
@pytest.fixture(autouse=True)
def cleanup_trades(api_client):
    """Automatically clean up any trades created during the test."""
    created_trade_ids = []
    yield created_trade_ids
    for trade_id in created_trade_ids:
        api_client.delete_trade(trade_id)
```

- **Never leave orphaned test data** in shared environments (QA, STAGING)
- If a test creates a counterparty, it must also delete it in teardown
- Teardown failures are logged as warnings but do not fail the test (to avoid cascading failures)

## Regression Suite

- The regression suite runs **nightly at 11:00 PM EST** via GitHub Actions
- Results are posted automatically to the **#qa-regression-results** Slack channel
- The suite covers approximately **450+ test cases** across all clearing modules
- Execution time target: under **45 minutes**
- Any test failure blocks the next day's deployment pipeline until resolved

### Regression Suite Structure
| Module | Test Count | Approximate Runtime |
|--------|-----------|-------------------|
| Trade Submission | 85 tests | ~8 min |
| Trade Matching | 65 tests | ~6 min |
| Clearing & Novation | 120 tests | ~12 min |
| Settlement | 90 tests | ~10 min |
| Reference Data | 45 tests | ~4 min |
| Authentication & Authorization | 35 tests | ~3 min |
| Smoke Tests (critical path) | 10 tests | ~2 min |

### Running Specific Modules
```bash
# Run only clearing tests
pytest tests/ -v -m "clearing"

# Run smoke tests (fast, critical path only)
pytest tests/ -v -m "smoke"

# Run nightly regression locally
pytest tests/ -v -m "regression"

# Run with Allure reporting
pytest tests/ -v --alluredir=./allure-results
allure serve ./allure-results
```

## Regulatory Scenario Testing

ICE operates under strict regulatory oversight. The following regulatory scenarios must be tested:

- **Position limits:** Verify the system enforces position limits per instrument and per account
- **Large trader reporting:** Verify that trades exceeding reporting thresholds are flagged automatically
- **Trade reconciliation:** Verify end-of-day reconciliation between clearing and exchange records
- **Audit trail:** Verify all trade modifications are logged with timestamp, user ID, and reason
- **Regulatory reporting:** Verify daily, weekly, and monthly regulatory reports are generated correctly

## Severity Definitions

| Severity | Name | Description | Response Time | Example |
|----------|------|-------------|---------------|---------|
| S1 | Critical | Trade processing is blocked entirely | Immediate (< 1 hour) | Clearing engine crash, trades not matching |
| S2 | Major | Data mismatch or incorrect calculations | Same day (< 4 hours) | Wrong margin calculation, settlement amount discrepancy |
| S3 | Minor | UI issue affecting usability | Within sprint (< 5 days) | Dashboard widget not loading, report formatting issue |
| S4 | Cosmetic | Visual-only issue, no functional impact | Backlog | Misaligned text, wrong icon color |

### Severity Decision Guide
When in doubt about severity, ask:
- **Could this cause financial loss?** → S1 or S2
- **Could this delay a trade or settlement?** → S1 or S2
- **Does it affect data accuracy?** → S2
- **Can the user work around it?** → S3
- **Is it only visual?** → S4

## Bug Reporting

All bugs are reported in **Jira** under the project **ICE-QA**.

### Required Fields
- **Summary**: Clear, concise description of the defect
- **Severity**: S1, S2, S3, or S4 (see definitions above)
- **Environment**: Which environment the bug was found in (DEV, QA, STAGING)
- **Steps to Reproduce**: Numbered, specific steps
- **Expected Result**: What should happen
- **Actual Result**: What actually happens
- **Attachments**: Screenshots, logs, and/or video recordings

### Bug Report Template
```
Summary: [Brief description]
Severity: [S1/S2/S3/S4]
Environment: [DEV/QA/STAGING]
Build/Version: [e.g., v2.4.1-rc3]
Browser/Client: [e.g., Chrome 120, Playwright 1.42]

Steps to Reproduce:
1. Navigate to...
2. Click on...
3. Enter...

Expected Result: [What should happen]
Actual Result: [What actually happens]

Attachments: [Screenshots, logs, trace files]
Related Test Case: [Link to automated test if applicable]
```

### Escalation Path
- **S1 bugs:** Immediately notify QA Lead + Engineering Lead via Slack AND Jira. Page the on-call engineer if during off-hours.
- **S2 bugs:** Notify QA Lead within 4 hours, assign to current sprint
- **S3/S4 bugs:** Triage in next Tuesday bug triage session

### Bug Lifecycle
```
Open → In Progress → Fixed → Verified → Closed
                    → Won't Fix → Closed
                    → Duplicate → Closed
```
- **Verified:** QA confirms the fix resolves the issue in the same environment where it was found
- **Won't Fix:** Engineering decides the issue is by design or too risky to change — requires QA Lead agreement
- **Duplicate:** Link to the original bug when closing as duplicate
