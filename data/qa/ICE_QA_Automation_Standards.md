# ICE QA Automation Standards

## Primary Framework

The QA Automation team uses **Playwright with Python bindings** as the primary end-to-end testing framework. All new test automation must use Playwright unless an exception is approved by the QA Lead (Sarah Chen).

### Why Playwright?
- Cross-browser testing (Chromium, Firefox, WebKit) from a single API
- Built-in auto-waiting eliminates flaky selectors
- Network interception for API mocking and monitoring
- Trace viewer for debugging failed tests
- Native support for multiple browser contexts (parallel testing)

## Test Structure — Page Object Model (POM)

All UI tests must follow the **Page Object Model** pattern:

```
tests/
├── pages/
│   ├── login_page.py
│   ├── dashboard_page.py
│   ├── trade_entry_page.py
│   └── clearing_page.py
├── tests/
│   ├── test_login_scenarios.py
│   ├── test_dashboard_widgets.py
│   └── test_trade_lifecycle.py
├── fixtures/
│   ├── conftest.py
│   └── test_data.py
└── utils/
    ├── api_helpers.py
    └── db_helpers.py
```

### Page Object Rules
- Each page class encapsulates all locators and actions for a single page
- Page objects should expose meaningful methods (e.g., `login(username, password)`) not raw selectors
- Locators must use `data-testid` attributes as the primary strategy, falling back to accessible roles
- Never use XPath unless absolutely necessary (fragile, hard to maintain)
- Page objects must not contain assertions — assertions belong in test files only
- Constructor should accept a Playwright `Page` object and store it as `self.page`

### Page Object Example
```python
class LoginPage:
    """Page object for the ICE login screen."""
    
    def __init__(self, page):
        self.page = page
        self.username_input = page.locator("[data-testid='username']")
        self.password_input = page.locator("[data-testid='password']")
        self.login_button = page.locator("[data-testid='login-submit']")
        self.error_message = page.locator("[data-testid='login-error']")
    
    def navigate(self):
        self.page.goto("/login")
        return self
    
    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        return self
    
    def get_error_text(self) -> str:
        return self.error_message.text_content()
```

## Playwright Fixtures

All tests should use pytest fixtures for browser and page setup. Our standard fixtures are in `conftest.py`:

### Browser & Page Fixtures
```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    """Launch browser once per test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    """Create a new page for each test."""
    context = browser.new_context(
        base_url="https://qa-clearing.ice-internal.com",
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()
    yield page
    context.close()

@pytest.fixture
def authenticated_page(page):
    """Page with a logged-in test user."""
    page.goto("/login")
    page.fill("[data-testid='username']", os.environ["ICE_TEST_USER"])
    page.fill("[data-testid='password']", os.environ["ICE_TEST_PASSWORD"])
    page.click("[data-testid='login-submit']")
    page.wait_for_url("**/dashboard")
    return page
```

## Naming Conventions

- Test files: `test_<module>_<scenario>.py`
  - Example: `test_clearing_trade_lifecycle.py`
- Test functions: `test_<action>_<expected_outcome>`
  - Example: `test_submit_trade_returns_confirmation_id`
- Page objects: `<PageName>Page`
  - Example: `ClearingPage`, `LoginPage`
- Fixture files: Descriptive names in `fixtures/` directory
  - Example: `trade_data_fixtures.py`, `auth_fixtures.py`

## Assertions

- **Always use Playwright's `expect()` API** over raw Python `assert` statements
- `expect()` provides auto-waiting, better error messages, and retry logic
- Standard timeout: 5 seconds (configurable per assertion)

```python
# ✅ GOOD — auto-waits, clear error messages
expect(page.locator("#status")).to_have_text("Cleared")
expect(page.locator("#trade-table")).to_be_visible()
expect(page.locator("#amount")).to_contain_text("$1,000.00")

# ❌ BAD — no auto-wait, generic error
assert page.locator("#status").text_content() == "Cleared"
```

### Common Assertion Patterns
```python
# Check element is visible
expect(page.locator("#success-banner")).to_be_visible()

# Check text content
expect(page.locator("#status")).to_have_text("Trade Submitted")

# Check element count (e.g., table rows)
expect(page.locator("table tbody tr")).to_have_count(5)

# Check URL after navigation
expect(page).to_have_url("**/dashboard")

# Check input value
expect(page.locator("#trade-id")).to_have_value("ICE-2024-001")
```

## Test Data Management

- **Use fixtures** for all test data — defined in `conftest.py` or dedicated fixture files
- **Never hardcode** test data (usernames, trade IDs, amounts) directly in test functions
- Use the synthetic trade generator (`/tools/trade-gen`) for realistic test data
- Sensitive data (even test credentials) must be loaded from **environment variables or CyberArk**
- Test data filenames: `test_data_<module>.json` or `test_data_<module>.py`

### Test Data Example
```python
# In fixtures/test_data.py
VALID_TRADE = {
    "instrument": "ESM2024",
    "side": "BUY",
    "quantity": 10,
    "price": 5120.50,
    "counterparty": "TEST_CP_001",
}

INVALID_TRADE_MISSING_PRICE = {
    "instrument": "ESM2024",
    "side": "BUY",
    "quantity": 10,
    "counterparty": "TEST_CP_001",
}
```

## Handling Flaky Tests

- Flaky tests must be investigated **immediately** — do not use `@pytest.mark.skip` to hide failures
- If a test is genuinely flaky due to timing, add appropriate `expect()` waits rather than `time.sleep()`
- **Never use `time.sleep()`** in test code — always use Playwright's built-in waiting mechanisms
- If a test is flaky due to environment instability, report it in #qa-environments and mark with `@pytest.mark.flaky(reason="ENV-1234")`
- Flaky test metrics are tracked — any test that fails more than 3 times in 2 weeks without a code change is flagged for review

## Retry Policy
```python
# In pytest.ini or conftest.py — retries for CI only
# Do NOT use retries to mask flaky tests
[pytest]
; Retries are configured in CI only — not for local development
; Maximum 1 retry for infrastructure-related failures
```

## Visual Regression Testing

- Visual regression tests use **Playwright's screenshot comparison** feature
- Baseline screenshots are stored in `tests/visual_baselines/`
- Threshold: **0.1% pixel difference** tolerance (accounts for anti-aliasing differences across environments)
- Update baselines: `pytest --update-snapshots` (requires QA Lead approval for PR)

## Accessibility Testing

- All new UI features must include basic accessibility checks
- Use Playwright's `page.accessibility.snapshot()` for accessibility tree validation
- Minimum requirements: All interactive elements must have accessible names, proper ARIA labels, and keyboard navigability
- Accessibility violations are treated as **S3 (Minor)** bugs unless they block screen reader users (then S2)

## CI Integration

- All tests run on **GitHub Actions** as part of the CI pipeline
- Tests must pass before a PR can be merged (branch protection rule)
- The CI pipeline runs:
  1. Linting (flake8 + black formatting check) — ~2 min
  2. Unit tests (pytest) — ~5 min
  3. Integration tests (Playwright) — ~15 min
  4. Test report generation (Allure) — ~1 min
- Flaky tests must be investigated immediately — do not use `@pytest.mark.skip` to hide failures
- CI test results and Allure reports are attached to the PR as comments

## Code Review Standards

- Every test PR requires at least **1 approval** from another QA engineer
- Reviewers should check:
  - POM pattern compliance
  - Proper use of `expect()` assertions (no raw `assert`)
  - No hardcoded test data
  - Meaningful test names that describe behavior, not implementation
  - Proper teardown/cleanup
  - No `time.sleep()` calls
  - No XPath selectors
- Review turnaround SLA: **24 hours**

## Mocking & Stubbing

- Use Playwright's `page.route()` for API mocking in UI tests
- External service dependencies should be mocked in integration tests
- Never mock the system under test — only its dependencies
- Mock data should be realistic (use the trade generator when possible)

```python
# Mock API response in Playwright
async def mock_trade_api(route):
    await route.fulfill(json={"trade_id": "TEST-001", "status": "Cleared"})

page.route("**/api/v1/trades", mock_trade_api)
```

## Test Reporting

- All test results are reported via **Allure**
- Tests should use Allure decorators for better report organization:
  - `@allure.feature("Clearing")` — high-level feature area
  - `@allure.story("Trade Submission")` — specific user story
  - `@allure.severity(allure.severity_level.CRITICAL)` — severity classification
- Attach screenshots on failure (configured automatically in conftest.py)
- Nightly regression results are posted to **#qa-regression-results** Slack channel
