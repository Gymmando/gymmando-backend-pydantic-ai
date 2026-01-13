# Load Testing with Locust

This directory contains load tests for the Gymmando API using [Locust](https://locust.io/).

## Setup

1. Install dependencies:
   ```bash
   pip install -r tests/load/requirements.txt
   ```

## Running Tests

### Basic Usage

From the `tests/load/` directory:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

Or from the project root:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

### Web UI

After running the command above, open your browser to:
- http://localhost:8089

From the web UI you can:
- Set number of users to simulate
- Set spawn rate (users per second)
- Start/stop tests
- View real-time statistics

### Headless Mode (No UI)

```bash
locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 60s
```

Options:
- `-u 100`: 100 concurrent users
- `-r 10`: Spawn 10 users per second
- `-t 60s`: Run for 60 seconds

## Current Tests

### Token Endpoint (`/token`)
Tests the LiveKit token generation endpoint with varying user IDs.

## Environment

Make sure your API server is running before starting load tests:
```bash
# In another terminal
cd gymmando-backend
uvicorn gymmando_api.main:app --reload --port 8000
```

### Verify API is Running

Test the endpoint manually first:
```bash
curl http://localhost:8000/token?user_id=test123
```

You should get a JSON response with a `token` field.

## Troubleshooting

### 100% Failure Rate

1. **Check if API is running:**
   ```bash
   curl http://localhost:8000/token?user_id=test123
   ```

2. **Check the host URL:**
   - Make sure `--host` matches where your API is running
   - Default: `http://localhost:8000`

3. **Check Locust error details:**
   - In Locust web UI, click "Failures" tab
   - Look for specific error messages (Connection refused, 404, 500, etc.)

4. **Check API logs:**
   - Look at the terminal where uvicorn is running
   - Check for error messages or exceptions

5. **Environment variables:**
   - Make sure `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are set
   - The `/token` endpoint needs these to generate tokens

## Testing Different Environments

Change the `--host` parameter to test different environments:
- Local: `--host=http://localhost:8000`
- Staging: `--host=https://your-staging-url.com`
- Production: `--host=https://your-production-url.com` (use with caution!)
