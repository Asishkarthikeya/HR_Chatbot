# ICE API Testing Guide

## API Testing Framework

The QA team uses **pytest** with the **requests** library for all API testing. This combination provides:
- Flexible test organization with fixtures and parameterization
- Easy HTTP request handling
- Rich assertion capabilities
- Integration with the CI/CD pipeline

## Project Structure

```
api_tests/
├── conftest.py              # Shared fixtures (auth tokens, base URLs, cleanup)
├── test_trade_api.py        # Trade submission and lifecycle endpoints
├── test_clearing_api.py     # Clearing and novation endpoints
├── test_settlement_api.py   # Settlement and reconciliation endpoints
├── test_reference_data.py   # Instrument and counterparty lookups
├── helpers/
│   ├── auth.py              # OAuth2 token management
│   └── assertions.py        # Custom API assertion helpers
└── data/
    └── payloads.py          # Request payload templates
```

## Authentication

- All ICE internal APIs use **OAuth2 bearer tokens**
- Tokens are obtained from the internal auth service at `https://auth.ice-internal.com/oauth2/token`
- **Never hardcode tokens** in test code or configuration files
- Use a pytest fixture to manage token lifecycle:

```python
@pytest.fixture(scope="session")
def auth_token():
    """Obtain OAuth2 token for API testing."""
    client_id = os.environ["ICE_API_CLIENT_ID"]
    client_secret = os.environ["ICE_API_CLIENT_SECRET"]
    response = requests.post(
        "https://auth.ice-internal.com/oauth2/token",
        data={"grant_type": "client_credentials",
              "client_id": client_id,
              "client_secret": client_secret}
    )
    return response.json()["access_token"]
```

- Store client credentials in **CyberArk** or environment variables — never in code

## FIX Protocol Testing

The Financial Information eXchange (FIX) protocol is used for trade communication.

### Testing Rules
- Use the **QuickFIX simulator** for all FIX protocol testing
- **NEVER connect to the live FIX gateway** from test environments
- The QuickFIX simulator runs at `fix-sim.ice-internal.com:9876`
- Supported FIX versions: FIX 4.2, FIX 4.4, FIX 5.0 SP2

### Common FIX Test Scenarios
- New Order Single (MsgType=D) — validate order submission
- Execution Report (MsgType=8) — validate trade confirmation
- Order Cancel Request (MsgType=F) — validate cancellation flow
- Reject (MsgType=3) — validate error handling for malformed messages

## Contract Testing

The QA team uses **Pact** for consumer-driven contract testing between microservices.

### How It Works
1. **Consumer tests** define expected API interactions (request/response pairs)
2. Pact generates a **contract file** (JSON) from consumer tests
3. **Provider verification** runs the contract against the actual provider API
4. Contract files are stored in the **Pact Broker** at `https://pact-broker.ice-internal.com`

### When to Write Contract Tests
- Whenever a service depends on another service's API
- Before making breaking changes to an API endpoint
- As part of the PR review checklist for any API changes

## API Test Best Practices

1. **Test independence**: Each test must be runnable in isolation — no dependency on test execution order
2. **Idempotency**: Tests should produce the same result regardless of how many times they run
3. **Clean data**: Create test data in setup, clean it up in teardown
4. **Meaningful assertions**: Check status codes, response body structure, and business logic — not just "200 OK"
5. **Error scenarios**: Test 400, 401, 403, 404, and 500 responses explicitly
6. **Response time**: API tests should assert response time is under **2 seconds** for standard endpoints

## Running API Tests

```bash
# Run all API tests
pytest api_tests/ -v

# Run specific test file
pytest api_tests/test_trade_api.py -v

# Run with specific environment
ICE_ENV=qa pytest api_tests/ -v

# Generate Allure report
pytest api_tests/ --alluredir=./allure-results
```
