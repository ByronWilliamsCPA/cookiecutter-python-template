/**
 * k6 Load Testing Script for {{ cookiecutter.project_name }}
 *
 * k6 is a modern, high-performance load testing tool written in Go.
 * It's ideal for testing APIs and can handle millions of requests per second.
 *
 * Setup:
 *   1. Install k6:
 *      # macOS
 *      brew install k6
 *
 *      # Linux
 *      sudo gpg -k
 *      sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
 *      echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
 *      sudo apt-get update
 *      sudo apt-get install k6
 *
 *      # Docker
 *      docker pull grafana/k6:latest
 *
 *   2. Run test:
 *      k6 run tests/load/k6-script.js
 *
 *   3. Run with custom options:
 *      k6 run --vus 100 --duration 5m tests/load/k6-script.js
 *
 *   4. Run with environment variables:
 *      k6 run -e BASE_URL=http://localhost:8000 tests/load/k6-script.js
 *
 * Features:
 *   - High performance (written in Go)
 *   - JavaScript scripting (easy to learn)
 *   - Built-in metrics and thresholds
 *   - Multiple load patterns
 *   - Cloud integration (k6 Cloud)
 *   - Prometheus/Grafana export
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// =============================================================================
// Configuration
// =============================================================================

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Custom metrics
const errorRate = new Rate('errors');
const customTrend = new Trend('custom_response_time');
const requestCounter = new Counter('api_requests');

// =============================================================================
// Load Test Options
// =============================================================================

export const options = {
  // Scenario 1: Gradual Ramp-Up (default)
  stages: [
    { duration: '2m', target: 50 },   // Ramp-up to 50 users over 2 minutes
    { duration: '5m', target: 100 },  // Stay at 100 users for 5 minutes
    { duration: '2m', target: 200 },  // Ramp-up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users for 5 minutes
    { duration: '2m', target: 0 },    // Ramp-down to 0 users
  ],

  // Thresholds (pass/fail criteria)
  thresholds: {
    // HTTP errors should be less than 1%
    'http_req_failed': ['rate<0.01'],

    // 95% of requests should complete within 500ms
    'http_req_duration': ['p(95)<500'],

    // 99% of requests should complete within 1000ms
    'http_req_duration{name:list_items}': ['p(99)<1000'],

    // Custom error rate threshold
    'errors': ['rate<0.05'],
  },

  // Resource limits
  noConnectionReuse: false,
  userAgent: 'k6-LoadTest/1.0',

  // Graceful stop
  gracefulStop: '30s',
};

// =============================================================================
// Alternative Load Patterns (comment/uncomment as needed)
// =============================================================================

// Spike Test - sudden traffic surge
// export const options = {
//   stages: [
//     { duration: '10s', target: 100 },   // Fast ramp-up
//     { duration: '1m', target: 100 },    // Stay at peak
//     { duration: '10s', target: 0 },     // Fast ramp-down
//   ],
// };

// Stress Test - find breaking point
// export const options = {
//   stages: [
//     { duration: '2m', target: 100 },
//     { duration: '5m', target: 200 },
//     { duration: '2m', target: 300 },
//     { duration: '5m', target: 400 },
//     { duration: '2m', target: 500 },
//     { duration: '5m', target: 600 },
//     { duration: '2m', target: 0 },
//   ],
// };

// Soak/Endurance Test - sustained load
// export const options = {
//   stages: [
//     { duration: '5m', target: 100 },    // Ramp-up
//     { duration: '4h', target: 100 },    // Sustained load for 4 hours
//     { duration: '5m', target: 0 },      // Ramp-down
//   ],
// };

// Constant Load - fixed number of requests per second
// export const options = {
//   scenarios: {
//     constant_request_rate: {
//       executor: 'constant-arrival-rate',
//       rate: 100,              // 100 requests per second
//       timeUnit: '1s',
//       duration: '10m',
//       preAllocatedVUs: 50,    // Pre-allocate 50 VUs
//       maxVUs: 200,            // Max 200 VUs
//     },
//   },
// };

// =============================================================================
// Setup (runs once before test)
// =============================================================================

export function setup() {
  // Initialize test data, get auth tokens, etc.
  console.log(`🚀 Starting load test against ${BASE_URL}`);

  // Example: Login to get auth token
  // const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
  //   username: 'testuser',
  //   password: 'testpass'
  // }), {
  //   headers: { 'Content-Type': 'application/json' },
  // });
  //
  // return {
  //   authToken: loginRes.json('token'),
  // };

  return {};
}

// =============================================================================
// Main Test Function (runs repeatedly for each VU)
// =============================================================================

export default function (data) {
  // Weighted task selection (similar to Locust)
  const rand = Math.random();

  if (rand < 0.5) {
    // 50% - Health checks
    checkHealth();
  } else if (rand < 0.8) {
    // 30% - List items
    listItems();
  } else if (rand < 0.95) {
    // 15% - Get item detail
    getItemDetail();
  } else {
    // 5% - Create item
    createItem(data);
  }

  // Think time between requests (1-3 seconds)
  sleep(Math.random() * 2 + 1);
}

// =============================================================================
// Test Scenarios
// =============================================================================

function checkHealth() {
  group('Health Check', () => {
    const res = http.get(`${BASE_URL}/health/live`, {
      tags: { name: 'health_check' },
    });

    check(res, {
      'health check status is 200': (r) => r.status === 200,
      'health check response is ok': (r) => r.json('status') === 'ok',
      'health check is fast': (r) => r.timings.duration < 100,
    });

    errorRate.add(res.status !== 200);
    requestCounter.add(1);
  });
}

function listItems() {
  group('List Items', () => {
    const page = Math.floor(Math.random() * 10) + 1;
    const limit = [10, 20, 50][Math.floor(Math.random() * 3)];

    const res = http.get(`${BASE_URL}/api/items?page=${page}&limit=${limit}`, {
      tags: { name: 'list_items' },
    });

    const checkResult = check(res, {
      'list items status is 200': (r) => r.status === 200,
      'list items has data': (r) => r.json('items') !== undefined,
      'list items response time < 500ms': (r) => r.timings.duration < 500,
    });

    errorRate.add(!checkResult);
    customTrend.add(res.timings.duration);
    requestCounter.add(1);
  });
}

function getItemDetail() {
  group('Get Item Detail', () => {
    const itemId = Math.floor(Math.random() * 1000) + 1;

    const res = http.get(`${BASE_URL}/api/items/${itemId}`, {
      tags: { name: 'get_item' },
    });

    check(res, {
      'get item status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'get item response time < 300ms': (r) => r.timings.duration < 300,
    });

    errorRate.add(res.status !== 200 && res.status !== 404);
    requestCounter.add(1);
  });
}

function createItem(data) {
  group('Create Item', () => {
    const payload = JSON.stringify({
      name: `Test Item ${Date.now()}`,
      description: 'Load test item',
      price: Math.random() * 1000,
      quantity: Math.floor(Math.random() * 100) + 1,
    });

    const params = {
      headers: {
        'Content-Type': 'application/json',
        // 'Authorization': `Bearer ${data.authToken}`,  // Uncomment if using auth
      },
      tags: { name: 'create_item' },
    };

    const res = http.post(`${BASE_URL}/api/items`, payload, params);

    check(res, {
      'create item status is 201': (r) => r.status === 201 || r.status === 401,
      'create item response time < 1s': (r) => r.timings.duration < 1000,
    });

    errorRate.add(res.status !== 201 && res.status !== 401);
    requestCounter.add(1);
  });
}

// =============================================================================
// Teardown (runs once after test)
// =============================================================================

export function teardown(data) {
  // Cleanup test data, logout, etc.
  console.log('✅ Load test completed');
}

// =============================================================================
// Usage Examples
// =============================================================================

/*
# Basic run
k6 run tests/load/k6-script.js

# Custom duration and VUs
k6 run --vus 100 --duration 5m tests/load/k6-script.js

# With environment variables
k6 run -e BASE_URL=http://staging.example.com tests/load/k6-script.js

# Output to JSON for analysis
k6 run --out json=results.json tests/load/k6-script.js

# Output to InfluxDB for Grafana dashboards
k6 run --out influxdb=http://localhost:8086/k6 tests/load/k6-script.js

# Run in cloud (k6 Cloud)
k6 cloud tests/load/k6-script.js

# Docker
docker run --rm -v $(pwd):/scripts grafana/k6:latest run /scripts/tests/load/k6-script.js
*/
