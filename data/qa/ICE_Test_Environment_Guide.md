# ICE Test Environment Guide

## Environment Overview

| Environment | Purpose | URL | QA Access |
|------------|---------|-----|-----------| 
| DEV | Developer testing, feature branches | https://dev-clearing.ice-internal.com | Full read/write |
| QA | QA team testing, sprint validation | https://qa-clearing.ice-internal.com | Full read/write |
| STAGING | Pre-production validation, UAT | https://staging-clearing.ice-internal.com | Read-only |
| PROD | Live production | https://clearing.ice.com | Read-only (monitoring dashboards only) |

### When to Use Each Environment
- **DEV:** Use when developing new tests or testing against a specific feature branch. Data is volatile — expect resets.
- **QA:** Primary testing environment. Use for sprint testing, regression runs, and test case execution. Most stable non-prod environment.
- **STAGING:** Pre-release validation only. Used for UAT and final QA sign-off before production deployment. Do not create persistent test data here.
- **PROD:** Never test directly in production. QA has read-only access to monitoring dashboards (Grafana) for post-deployment verification only.

## VPN Requirements

- **VPN is required** for all non-PROD environments
- Use **Cisco AnyConnect** with your ICE credentials
- VPN profiles:
  - `ice-dev-vpn.ice-internal.com` — for DEV and QA access
  - `ice-staging-vpn.ice-internal.com` — for STAGING access
- If VPN connection fails, check with IT Help Desk (ext. 2-HELP)
- Multi-factor authentication (MFA) via **Duo Mobile** is required for all VPN connections

### VPN Troubleshooting
| Issue | Solution |
|-------|----------|
| "Unable to connect" | Ensure Cisco AnyConnect is updated to the latest version. Restart your laptop. |
| "Authentication failed" | Check your ICE credentials. If locked out, contact IT Help Desk (ext. 2-HELP). |
| "Connection timeout" | Try disconnecting and reconnecting. Check #qa-environments Slack channel for outage notices. |
| Connected but can't reach URLs | Verify you're on the correct VPN profile (dev vs staging). DNS may need to refresh — try `ipconfig /flushdns` or `sudo dscacheutil -flushcache`. |
| Duo push not arriving | Open the Duo Mobile app and ensure it's registered to your ICE account. Contact IT if re-registration is needed. |

## Environment Access Request Process

1. Go to **servicenow.ice-internal.com**
2. Click **"Request Something"** → **"IT Access Request"**
3. Fill in:
   - **Environment:** Select DEV, QA, or STAGING
   - **System:** Select from the dropdown (e.g., "Clearing Platform", "Trade Management")
   - **Access Level:** Read-only or Read/Write
   - **Business Justification:** "QA testing for sprint [sprint number]" is sufficient
   - **Manager Approval:** Auto-routed to your manager
4. Processing time:
   - DEV/QA access: **24–48 hours**
   - STAGING access: **2–3 business days** (requires additional security review)
   - CyberArk (database credentials): **Up to 3 business days**

## Test Data Guidelines

### Synthetic Data
- Use the **synthetic trade generator** at `/tools/trade-gen` to create realistic mock data
- The trade generator supports: equities, fixed income, derivatives, and clearing trades
- Generated data includes realistic but fictional: counterparty IDs, trade amounts, timestamps, and settlement dates
- The generator creates data in the correct format for each environment — no manual translation needed

### Trade Generator Usage
```bash
# Generate 100 synthetic equity trades
python tools/trade-gen --type equity --count 100 --env qa

# Generate derivative trades with specific date range
python tools/trade-gen --type derivative --count 50 --start-date 2024-01-01 --end-date 2024-03-31

# Reset all test data in QA environment
python tools/trade-gen --reset --env qa
```

### Critical Rules
- **NEVER use real market data** in any test environment
- **NEVER copy production data** to lower environments
- All test data must be clearly labeled with a `TEST_` prefix in relevant identifier fields
- Test accounts use the naming pattern: `test_user_<team>_<number>` (e.g., `test_user_qa_001`)
- Test counterparty IDs always start with `TEST_CP_` (e.g., `TEST_CP_001`)
- Never use real company names, real ticker symbols, or real trade amounts in test data

### Data Masking
- When production data is used for environment refreshes, all PII and sensitive financial data is automatically masked
- Masking is applied by the Data Engineering team before data loads
- Masked fields: customer names, account numbers, actual trade amounts, IP addresses
- If you encounter any unmasked production data in a lower environment, **report it immediately** to the Compliance team

## Database Access

| Environment | Access Level | Connection | How to Get Credentials |
|------------|-------------|------------|----------------------|
| DEV | Read/Write | Via DBeaver | CyberArk → "DEV Database" vault |
| QA | Read-only | Via DBeaver | CyberArk → "QA Database" vault |
| STAGING | No direct access | Request via ServiceNow | N/A — queries go through the API only |
| PROD | No access | Strictly prohibited for QA | N/A |

- Database credentials are **never stored in code or config files**
- All database access is logged and audited
- Use **CyberArk** to retrieve database credentials before each session — credentials rotate every 24 hours
- DBeaver connection profiles are pre-configured — ask your onboarding buddy to help set this up

## Feature Flags

- ICE uses **LaunchDarkly** for feature flag management
- In non-prod environments, QA has **read/write access** to feature flags
- In STAGING and PROD, only Engineering Leads can modify feature flags
- When testing a feature behind a flag:
  1. Enable the flag in DEV/QA for your test user
  2. Run your tests
  3. Disable the flag after testing (don't leave flags on for test users permanently)
- Flag naming convention: `enable-<feature-name>` (e.g., `enable-new-clearing-dashboard`)

## Containerized Local Development

For running tests locally without VPN (useful for writing tests on the go):

```bash
# Pull the local dev environment Docker image
docker pull ice-registry.ice-internal.com/qa-local-env:latest

# Start the containerized environment
docker-compose -f docker-compose.qa-local.yml up -d

# Run tests against the local container
ICE_ENV=local pytest tests/ -v

# Tear down
docker-compose -f docker-compose.qa-local.yml down
```

- The local container includes a mock clearing API and a test database
- It does **not** include real market data or FIX protocol connectivity
- Local environment is best for writing and debugging tests, not for official test execution

## Environment Refresh Schedule

- **DEV**: Refreshed weekly (Sunday midnight EST)
- **QA**: Refreshed bi-weekly (aligned with sprint boundaries, typically Saturday night)
- **STAGING**: Refreshed before each release candidate
- All refresh schedules are posted in the **#qa-environments** Slack channel
- After a refresh, you may need to recreate your test data — the trade generator makes this fast

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cannot reach DEV/QA URL | Check VPN connection, verify Cisco AnyConnect is active |
| 403 Forbidden | Your access request may be pending — check ServiceNow ticket status |
| Stale test data | Check the refresh schedule; manually trigger data reset via `/tools/trade-gen --reset` |
| Slow environment | Check #qa-environments for any ongoing maintenance notices |
| Database connection refused | Credentials may have rotated — retrieve fresh credentials from CyberArk |
| Tests pass locally but fail in CI | Check if the CI environment has different feature flags enabled. Verify environment variables. |
| Environment completely down | Check #qa-environments for outage notices. If none, report to DevOps via #devops-support |
