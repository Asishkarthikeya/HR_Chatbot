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

## Regression Suite

- The regression suite runs **nightly at 11:00 PM EST** via GitHub Actions
- Results are posted automatically to the **#qa-regression-results** Slack channel
- The suite covers approximately 450+ test cases across all clearing modules
- Execution time target: under 45 minutes
- Any test failure blocks the next day's deployment pipeline until resolved

## Severity Definitions

| Severity | Name | Description | Response Time | Example |
|----------|------|-------------|---------------|---------|
| S1 | Critical | Trade processing is blocked entirely | Immediate (< 1 hour) | Clearing engine crash, trades not matching |
| S2 | Major | Data mismatch or incorrect calculations | Same day (< 4 hours) | Wrong margin calculation, settlement amount discrepancy |
| S3 | Minor | UI issue affecting usability | Within sprint (< 5 days) | Dashboard widget not loading, report formatting issue |
| S4 | Cosmetic | Visual-only issue, no functional impact | Backlog | Misaligned text, wrong icon color |

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

Steps to Reproduce:
1. Navigate to...
2. Click on...
3. Enter...

Expected Result: [What should happen]
Actual Result: [What actually happens]

Attachments: [Screenshots, logs]
```

### Escalation Path
- S1 bugs: Immediately notify QA Lead + Engineering Lead via Slack and Jira
- S2 bugs: Notify QA Lead within 4 hours, assign to sprint
- S3/S4 bugs: Triage in next sprint planning session
