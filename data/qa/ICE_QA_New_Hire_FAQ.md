# ICE QA New Hire Technical FAQ

This document answers the most common technical questions new QA team members ask during their first few weeks at ICE.

## Getting Set Up

**Q: How do I clone the test automation repository?**
A: First, make sure your GitHub Enterprise access has been approved (check your ServiceNow ticket). Then:
```bash
git clone https://github.ice-internal.com/ice-engineering/qa-automation.git
cd qa-automation
pip install -r requirements.txt
playwright install
```
If you get a permission error, your access request is still pending. Check with your buddy or the IT Help Desk.

**Q: How do I run my first test?**
A: Once you've cloned the repo and installed dependencies:
```bash
# Make sure VPN is connected first
# Run a single test file
pytest tests/test_login_scenarios.py -v

# Run a specific test
pytest tests/test_login_scenarios.py::test_valid_login_succeeds -v

# Run all tests (full regression — takes ~15 minutes)
pytest tests/ -v
```

**Q: What Python version should I use?**
A: Python **3.11 or higher**. We recommend using `pyenv` to manage Python versions:
```bash
pyenv install 3.11.7
pyenv local 3.11.7
python --version  # Should show 3.11.7
```

**Q: How do I set up my local environment variables?**
A: Create a `.env` file in the repo root (it's in `.gitignore`, so it won't be committed):
```
ICE_ENV=qa
ICE_TEST_USER=test_user_qa_001
ICE_TEST_PASSWORD=<get from CyberArk>
ICE_API_CLIENT_ID=<get from CyberArk>
ICE_API_CLIENT_SECRET=<get from CyberArk>
```
Never commit this file. Get the values from CyberArk or ask your onboarding buddy.

## Day-to-Day Testing

**Q: How do I write a new test case?**
A: Follow the Page Object Model pattern:
1. Check if a page object already exists in `tests/pages/`. If not, create one.
2. Create a new test file in `tests/tests/` following the naming convention: `test_<module>_<scenario>.py`
3. Use fixtures from `conftest.py` for setup and teardown.
4. Use `expect()` for all assertions (not `assert`).
5. Run your test locally to verify it passes.
6. Submit a PR and request a review from another QA engineer.

**Q: How do I know what to test?**
A: Test assignments come from three places:
1. **Sprint planning:** Tests are assigned during the bi-weekly sprint planning session
2. **Bug fixes:** When a bug is fixed, the QA Lead may ask you to write a regression test
3. **New features:** Each new feature has acceptance criteria in the Jira ticket — write tests to validate those criteria

**Q: What's the difference between the Playwright tests and the API tests?**
A: 
- **Playwright tests** (in `tests/`) test the UI — they open a browser and interact with the web application
- **API tests** (in `api_tests/`) test the backend endpoints directly — they send HTTP requests and validate responses
- Both are important: Playwright catches UI bugs, API tests catch business logic bugs
- As a new hire, you'll likely start with Playwright tests and move to API tests after a few weeks

**Q: How do I debug a failing test?**
A: Multiple approaches:
1. **Read the error message** — Playwright's `expect()` gives descriptive failure messages
2. **Run in headed mode** — See the browser interaction: `pytest tests/test_file.py --headed`
3. **Use Playwright trace viewer** — Add `--tracing on` to capture a trace, then open with `playwright show-trace trace.zip`
4. **Add `page.pause()`** — Stops execution and opens the Playwright Inspector for interactive debugging
5. **Check the Allure report** — CI failures include screenshots and detailed logs

**Q: Who do I ask when I'm stuck on a test?**
A: Escalation path:
1. **Your onboarding buddy** — first point of contact for the first 4 weeks
2. **#qa-automation Slack channel** — the whole automation team monitors this
3. **Sarah Chen (QA Lead)** — for test strategy questions or when you need a decision
4. **#devops-support** — for environment or infrastructure issues

## Code Review & PRs

**Q: What's the PR review process?**
A: 
1. Create a branch: `feature/ICE-QA-1234-short-description` or `bugfix/ICE-QA-5678-description`
2. Write your test and commit
3. Push and create a Pull Request in GitHub
4. PR description must include: what you're testing, link to the Jira ticket, and any special setup needed
5. Request a review from at least **1 QA engineer**
6. Reviewers check: POM compliance, proper assertions, no hardcoded data, meaningful names, cleanup
7. After approval, CI runs automatically. If green, merge.
8. Review turnaround SLA: **24 hours**

**Q: What do reviewers look for?**
A: The review checklist:
- [ ] Page Object Model pattern followed?
- [ ] Using `expect()` instead of raw `assert`?
- [ ] No hardcoded test data?
- [ ] Test name describes the behavior (e.g., `test_submit_trade_returns_confirmation_id`)?
- [ ] Proper teardown/cleanup for created data?
- [ ] No `time.sleep()` calls (use Playwright's built-in waits)?
- [ ] No XPath selectors?
- [ ] CI pipeline passes?

**Q: What if CI fails on my PR?**
A: 
1. Check the GitHub Actions logs to see which step failed (lint, unit test, integration test, security scan)
2. If it's a **lint failure**: Run `black .` and `flake8 .` locally to fix formatting
3. If it's a **test failure**: Check the Allure report attached to the PR for details
4. If it's a **flaky test** (not your code): Note the test name and report in #qa-automation. You may need a QA Lead override.
5. If it's a **security scan failure** (Snyk): Review the vulnerability and fix or get exception approval

## Environment & Infrastructure

**Q: Which environment should I test in?**
A: 
- **Writing new tests:** DEV (most flexible, full read/write)
- **Running tests for sprint validation:** QA (primary testing environment)
- **Running tests before a release:** STAGING (read-only, final validation)
- **Never:** PROD (read-only monitoring dashboards only)

**Q: What if the QA environment is down?**
A: 
1. Check **#qa-environments** Slack channel for any announced outages
2. If no announcement, report in #qa-environments and tag @devops-oncall
3. Switch to DEV environment temporarily: `ICE_ENV=dev pytest tests/ -v`
4. If both DEV and QA are down, use the local Docker container (see Test Environment Guide)

**Q: How do I get database access?**
A: 
1. Submit a ServiceNow request for CyberArk access (takes up to 3 business days)
2. Once approved, open CyberArk and find the "DEV Database" or "QA Database" vault
3. Copy the credentials (they rotate every 24 hours)
4. Connect using DBeaver — your buddy can help set up the connection profile
5. Remember: QA database is **read-only**. DEV is read/write.

## Testing the FIX Protocol

**Q: How do I test FIX messages?**
A: Use the **QuickFIX simulator** for all FIX protocol testing:
- Simulator URL: `fix-sim.ice-internal.com:9876`
- Supported versions: FIX 4.2, FIX 4.4, FIX 5.0 SP2
- **NEVER** connect to the live FIX gateway from test environments
- Common test scenarios: New Order Single (MsgType=D), Execution Report (MsgType=8), Order Cancel (MsgType=F), Reject (MsgType=3)
- FIX testing documentation is on Confluence under "QA → FIX Protocol Testing"

## Jira & Bug Reporting

**Q: How do I file a bug in Jira?**
A: 
1. Go to **Jira** → Project **ICE-QA** → Create Issue → Bug
2. Required fields:
   - **Summary:** Clear, concise (e.g., "Clearing dashboard shows wrong margin amount for derivative trades")
   - **Severity:** S1 (Critical), S2 (Major), S3 (Minor), S4 (Cosmetic)
   - **Environment:** DEV / QA / STAGING
   - **Steps to Reproduce:** Numbered, specific steps
   - **Expected vs. Actual Result**
   - **Attachments:** Screenshots, logs, video recordings
3. Assign to the appropriate engineering team or leave unassigned (bug triage will handle it)
4. S1 bugs: Immediately notify QA Lead + Engineering Lead via Slack AND Jira

**Q: How do I know the severity?**
A:
- **S1 (Critical):** Trade processing blocked entirely, system crash, data loss → Immediate response (<1 hour)
- **S2 (Major):** Data mismatch, wrong calculations, security vulnerability → Same day (<4 hours)
- **S3 (Minor):** UI issue affecting usability but work can continue → Within sprint (<5 days)
- **S4 (Cosmetic):** Visual-only issue, no functional impact → Backlog
- When in doubt, ask in the Tuesday bug triage meeting or ping the QA Lead.
