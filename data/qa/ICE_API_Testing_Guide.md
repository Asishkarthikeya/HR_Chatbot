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
    assert response.status_code == 200, f"Auth failed: {response.text}"
    return response.json()["access_token"]

@pytest.fixture
def api_client(auth_token):
    """Authenticated API client with base URL and headers."""
    base_url = os.environ.get("ICE_API_BASE_URL", "https://qa-clearing.ice-internal.com/api/v1")
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "X-Request-Source": "qa-automation"
    })
    session.base_url = base_url
    return session
```

- Store client credentials in **CyberArk** or environment variables — never in code

## API Endpoints Under Test

### Trade API (`/api/v1/trades`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/trades` | Submit a new trade |
| GET | `/trades/{trade_id}` | Get trade by ID |
| GET | `/trades?status=pending` | List trades by status |
| PUT | `/trades/{trade_id}/cancel` | Cancel a trade |
| GET | `/trades/{trade_id}/history` | Get trade audit history |

### Clearing API (`/api/v1/clearing`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/clearing/novate` | Novate a matched trade |
| GET | `/clearing/{clearing_id}` | Get clearing status |
| GET | `/clearing/margin/{account_id}` | Get margin requirements |
| POST | `/clearing/settle` | Initiate settlement |

### Reference Data API (`/api/v1/reference`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reference/instruments` | List all instruments |
| GET | `/reference/instruments/{symbol}` | Get instrument details |
| GET | `/reference/counterparties` | List counterparties |

## Writing API Tests

### Basic Test Pattern
```python
def test_submit_trade_returns_201(api_client):
    """Verify that a valid trade submission returns 201 Created."""
    payload = {
        "instrument": "ESM2024",
        "side": "BUY",
        "quantity": 10,
        "price": 5120.50,
        "counterparty": "TEST_CP_001"
    }
    response = api_client.post(f"{api_client.base_url}/trades", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "trade_id" in data
    assert data["status"] == "pending"
    assert data["instrument"] == "ESM2024"
```

### Testing Error Scenarios
```python
def test_submit_trade_missing_price_returns_400(api_client):
    """Verify that a trade without price returns 400 Bad Request."""
    payload = {
        "instrument": "ESM2024",
        "side": "BUY",
        "quantity": 10,
        "counterparty": "TEST_CP_001"
        # price intentionally omitted
    }
    response = api_client.post(f"{api_client.base_url}/trades", json=payload)
    
    assert response.status_code == 400
    assert "price" in response.json()["error"].lower()

def test_get_trade_invalid_id_returns_404(api_client):
    """Verify that requesting a non-existent trade returns 404."""
    response = api_client.get(f"{api_client.base_url}/trades/NONEXISTENT-ID")
    assert response.status_code == 404

def test_submit_trade_unauthorized_returns_401():
    """Verify that an unauthenticated request returns 401."""
    response = requests.post(
        "https://qa-clearing.ice-internal.com/api/v1/trades",
        json={"instrument": "ESM2024"}
    )
    assert response.status_code == 401
```

### Using Parameterized Tests
```python
@pytest.mark.parametrize("instrument,expected_type", [
    ("ESM2024", "future"),
    ("AAPL", "equity"),
    ("EUR/USD", "fx"),
    ("ICE-BRN-FUT", "commodity"),
])
def test_instrument_lookup_returns_correct_type(api_client, instrument, expected_type):
    """Verify instrument type classification for different asset classes."""
    response = api_client.get(f"{api_client.base_url}/reference/instruments/{instrument}")
    assert response.status_code == 200
    assert response.json()["type"] == expected_type
```

## Response Time Assertions

- API tests should assert response time is under **2 seconds** for standard endpoints
- Batch endpoints and reports may have higher thresholds (document in the test)

```python
def test_trade_submission_responds_within_2_seconds(api_client):
    payload = {"instrument": "ESM2024", "side": "BUY", "quantity": 10, "price": 5120.50, "counterparty": "TEST_CP_001"}
    response = api_client.post(f"{api_client.base_url}/trades", json=payload)
    assert response.elapsed.total_seconds() < 2.0, f"Response took {response.elapsed.total_seconds():.2f}s"
```

## Pagination Testing

For endpoints that return lists, always test pagination:

```python
def test_trades_list_pagination(api_client):
    """Verify pagination works correctly for trade listings."""
    # Get first page
    response = api_client.get(f"{api_client.base_url}/trades?page=1&per_page=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 10
    assert "total_count" in data
    assert "page" in data
    assert "per_page" in data
    
    # Verify last page doesn't exceed total
    if data["total_count"] > 10:
        last_page = (data["total_count"] // 10) + 1
        response = api_client.get(f"{api_client.base_url}/trades?page={last_page}&per_page=10")
        assert response.status_code == 200
```

## Rate Limiting Testing

```python
def test_rate_limit_returns_429(api_client):
    """Verify that exceeding the rate limit returns 429 Too Many Requests."""
    # The API rate limit is 100 requests per minute per client
    for _ in range(105):
        response = api_client.get(f"{api_client.base_url}/reference/instruments")
    assert response.status_code == 429
    assert "retry-after" in response.headers
```

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

### Contract Test Workflow
```bash
# Step 1: Write consumer test (defines expected interaction)
pytest contract_tests/consumer/ -v

# Step 2: Generate Pact contract file
# (Automatically created in pacts/ directory after consumer test runs)

# Step 3: Publish contract to Pact Broker
pact-broker publish pacts/ --broker-base-url https://pact-broker.ice-internal.com

# Step 4: Provider verification (run by the provider team's CI pipeline)
pytest contract_tests/provider/ -v --pact-broker-url https://pact-broker.ice-internal.com
```

## API Test Best Practices

1. **Test independence**: Each test must be runnable in isolation — no dependency on test execution order
2. **Idempotency**: Tests should produce the same result regardless of how many times they run
3. **Clean data**: Create test data in setup, clean it up in teardown
4. **Meaningful assertions**: Check status codes, response body structure, and business logic — not just "200 OK"
5. **Error scenarios**: Test 400, 401, 403, 404, and 500 responses explicitly
6. **Response time**: API tests should assert response time is under **2 seconds** for standard endpoints
7. **Headers**: Always verify content-type and other important response headers
8. **Schema validation**: Consider using a JSON schema validator for complex response bodies

## Test Data Cleanup

Always clean up test data to prevent test pollution:

```python
@pytest.fixture
def created_trade(api_client):
    """Create a trade for testing and clean up after."""
    payload = {"instrument": "ESM2024", "side": "BUY", "quantity": 10, "price": 5120.50, "counterparty": "TEST_CP_001"}
    response = api_client.post(f"{api_client.base_url}/trades", json=payload)
    trade_id = response.json()["trade_id"]
    yield trade_id
    # Cleanup
    api_client.put(f"{api_client.base_url}/trades/{trade_id}/cancel")
```

## Running API Tests

```bash
# Run all API tests
pytest api_tests/ -v

# Run specific test file
pytest api_tests/test_trade_api.py -v

# Run with specific environment
ICE_ENV=qa pytest api_tests/ -v

# Run with specific marker
pytest api_tests/ -v -m "smoke"

# Generate Allure report
pytest api_tests/ --alluredir=./allure-results

# Run in parallel (requires pytest-xdist)
pytest api_tests/ -v -n 4
```
