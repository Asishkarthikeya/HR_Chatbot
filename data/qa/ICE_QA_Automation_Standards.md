# ICE QA Automation Standards

## Primary Framework

The QA Automation team uses **Playwright with Python bindings** as the primary end-to-end testing framework. All new test automation must use Playwright unless an exception is approved by the QA Lead.

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
- Never use XPath unless absolutely necessary

## Naming Conventions

- Test files: `test_<module>_<scenario>.py`
  - Example: `test_clearing_trade_lifecycle.py`
- Test functions: `test_<action>_<expected_outcome>`
  - Example: `test_submit_trade_returns_confirmation_id`
- Page objects: `<PageName>Page`
  - Example: `ClearingPage`, `LoginPage`

## Assertions

- **Always use Playwright's `expect()` API** over raw Python `assert` statements
- `expect()` provides auto-waiting, better error messages, and retry logic
- Example:
  ```python
  # Good
  expect(page.locator("#status")).to_have_text("Cleared")
  
  # Bad
  assert page.locator("#status").text_content() == "Cleared"
  ```

## Test Data Management

- **Use fixtures** for all test data — defined in `conftest.py` or dedicated fixture files
- **Never hardcode** test data (usernames, trade IDs, amounts) directly in test functions
- Use the synthetic trade generator (`/tools/trade-gen`) for realistic test data
- Sensitive data (even test credentials) must be loaded from environment variables or CyberArk

## CI Integration

- All tests run on **GitHub Actions** as part of the CI pipeline
- Tests must pass before a PR can be merged (branch protection rule)
- The CI pipeline runs:
  1. Linting (flake8)
  2. Unit tests (pytest)
  3. Integration tests (Playwright)
  4. Test report generation (Allure)
- Flaky tests must be investigated immediately — do not use `@pytest.mark.skip` to hide failures

## Code Review Standards

- Every test PR requires at least **1 approval** from another QA engineer
- Reviewers should check:
  - POM pattern compliance
  - Proper use of `expect()` assertions
  - No hardcoded test data
  - Meaningful test names
  - Proper teardown/cleanup
