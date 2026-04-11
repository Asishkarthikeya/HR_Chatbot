# ICE Test Environment Guide

## Environment Overview

| Environment | Purpose | URL | QA Access |
|------------|---------|-----|-----------|
| DEV | Developer testing, feature branches | https://dev-clearing.ice-internal.com | Full read/write |
| QA | QA team testing, sprint validation | https://qa-clearing.ice-internal.com | Full read/write |
| STAGING | Pre-production validation, UAT | https://staging-clearing.ice-internal.com | Read-only |
| PROD | Live production | https://clearing.ice.com | Read-only (monitoring dashboards only) |

## VPN Requirements

- **VPN is required** for all non-PROD environments
- Use **Cisco AnyConnect** with your ICE credentials
- VPN profiles:
  - `ice-dev-vpn.ice-internal.com` — for DEV and QA access
  - `ice-staging-vpn.ice-internal.com` — for STAGING access
- If VPN connection fails, check with IT Help Desk (ext. 2-HELP)
- Multi-factor authentication (MFA) via Duo is required for all VPN connections

## Test Data Guidelines

### Synthetic Data
- Use the **synthetic trade generator** at `/tools/trade-gen` to create realistic mock data
- The trade generator supports: equities, fixed income, derivatives, and clearing trades
- Generated data includes realistic but fictional: counterparty IDs, trade amounts, timestamps, and settlement dates

### Critical Rules
- **NEVER use real market data** in any test environment
- **NEVER copy production data** to lower environments
- All test data must be clearly labeled with a `TEST_` prefix in relevant identifier fields
- Test accounts use the naming pattern: `test_user_<team>_<number>` (e.g., `test_user_qa_001`)

## Database Access

| Environment | Access Level | Connection |
|------------|-------------|------------|
| DEV | Read/Write | Via DBeaver, credentials in CyberArk |
| QA | Read-only | Via DBeaver, credentials in CyberArk |
| STAGING | No direct access | Request via ServiceNow ticket |
| PROD | No access | Strictly prohibited for QA |

- Database credentials are **never stored in code or config files**
- All database access is logged and audited
- Use CyberArk to retrieve database credentials before each session

## Environment Refresh Schedule

- **DEV**: Refreshed weekly (Sunday midnight EST)
- **QA**: Refreshed bi-weekly (aligned with sprint boundaries)
- **STAGING**: Refreshed before each release candidate
- All refresh schedules are posted in the #qa-environments Slack channel

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cannot reach DEV/QA URL | Check VPN connection, verify Cisco AnyConnect is active |
| 403 Forbidden | Your access request may be pending — check ServiceNow ticket status |
| Stale test data | Check the refresh schedule; manually trigger data reset via `/tools/trade-gen --reset` |
| Slow environment | Check #qa-environments for any ongoing maintenance notices |
