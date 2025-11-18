# Load Testing Guide

This directory contains load testing configurations for {{ cookiecutter.project_name }}.

## Overview

Load testing helps you:
- **Identify performance bottlenecks** before they affect users
- **Validate scalability** of your application
- **Establish performance baselines** for monitoring
- **Test infrastructure** under realistic traffic
- **Detect memory leaks** and resource issues
- **Verify SLA compliance** (response times, availability)

## Available Tools

### 1. Locust (Python-based)

**Best For:**
- Python developers (easy to write tests)
- Complex user behavior simulation
- Distributed load testing
- Real-time web UI dashboard

**Quick Start:**
```bash
# Install
uv add --dev locust

# Run with web UI
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Run headless
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 5m --headless
```

**Features:**
- ✅ Python scripting (familiar syntax)
- ✅ Real-time web UI at http://localhost:8089
- ✅ Distributed testing across multiple machines
- ✅ Task weighting for realistic traffic patterns
- ✅ CSV/JSON export for analysis

### 2. k6 (Go-based)

**Best For:**
- High-performance testing (millions of requests)
- CI/CD integration
- Grafana/Prometheus monitoring
- Protocol testing (HTTP, WebSocket, gRPC)

**Quick Start:**
```bash
# Install (macOS)
brew install k6

# Install (Linux)
sudo apt-get install k6

# Run test
k6 run tests/load/k6-script.js

# Custom configuration
k6 run --vus 100 --duration 5m tests/load/k6-script.js
```

**Features:**
- ✅ Extremely high performance
- ✅ JavaScript scripting (easy to learn)
- ✅ Built-in metrics and thresholds
- ✅ Grafana Cloud integration
- ✅ Multiple load patterns (ramp, spike, stress)

---

## Load Test Scenarios

### 1. **Smoke Test** (Sanity Check)
Minimal load to verify the system works.

```bash
# Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
       --users 10 --spawn-rate 2 --run-time 1m --headless

# k6
k6 run --vus 10 --duration 1m tests/load/k6-script.js
```

**When:** Before every deployment
**Goal:** Verify no critical errors

### 2. **Load Test** (Normal Traffic)
Simulate expected traffic levels.

```bash
# Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 10m --headless

# k6
k6 run --vus 100 --duration 10m tests/load/k6-script.js
```

**When:** Weekly or before major releases
**Goal:** Validate performance under normal conditions

### 3. **Stress Test** (Find Breaking Point)
Gradually increase load until system fails.

```bash
# Locust - Progressive load
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
       --users 1000 --spawn-rate 50 --run-time 30m --headless

# k6 - Staged increase
# Edit k6-script.js to use "Stress Test" options
k6 run tests/load/k6-script.js
```

**When:** Quarterly or before capacity planning
**Goal:** Understand system limits

### 4. **Spike Test** (Traffic Surge)
Sudden traffic increase (e.g., sales, viral content).

```bash
# Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
       --users 500 --spawn-rate 100 --run-time 2m --headless

# k6 - Use "Spike Test" options in script
k6 run tests/load/k6-script.js
```

**When:** Before marketing campaigns
**Goal:** Verify auto-scaling works

### 5. **Soak/Endurance Test** (Memory Leaks)
Sustained load over long period.

```bash
# Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
       --users 200 --spawn-rate 10 --run-time 4h --headless

# k6 - Use "Soak Test" options in script
k6 run tests/load/k6-script.js
```

**When:** Monthly or before long events
**Goal:** Detect memory leaks, resource exhaustion

---

## Performance Metrics

### Key Metrics to Track

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| **Response Time (p95)** | < 200ms | < 500ms | > 1s |
| **Response Time (p99)** | < 500ms | < 1s | > 2s |
| **Error Rate** | < 0.1% | < 1% | > 5% |
| **Throughput** | > 1000 req/s | > 500 req/s | < 100 req/s |
| **CPU Usage** | < 60% | < 80% | > 90% |
| **Memory Usage** | < 70% | < 85% | > 95% |

### SLA Examples
```bash
# 95th percentile < 500ms
# 99% uptime
# Error rate < 1%
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Load Test

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start application
        run: docker-compose up -d

      - name: Install k6
        run: |
          sudo gpg -k
          curl -s https://dl.k6.io/key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/k6-archive-keyring.gpg
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run load test
        run: k6 run --vus 50 --duration 5m tests/load/k6-script.js

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: load-test-results
          path: results.json
```

---

## Analyzing Results

### Locust Web UI
1. Navigate to http://localhost:8089
2. View real-time charts:
   - Total requests per second
   - Response times (median, 95th, 99th percentile)
   - Number of users
   - Failures

### k6 Console Output
```
checks.........................: 99.54% ✓ 9954      ✗ 46
data_received..................: 4.3 MB 860 kB/s
data_sent......................: 1.7 MB 340 kB/s
http_req_blocked...............: avg=1.07ms   min=1µs     med=5µs      max=124.05ms p(90)=9µs      p(95)=13µs
http_req_duration..............: avg=47.31ms  min=3.69ms  med=39.41ms  max=423.21ms p(90)=85.59ms  p(95)=107.97ms
http_reqs......................: 10000  2000/s
vus............................: 100    min=1       max=100
```

### Export to Grafana

**k6 + InfluxDB + Grafana:**
```bash
# Start InfluxDB
docker run -d -p 8086:8086 influxdb:1.8

# Run k6 with InfluxDB output
k6 run --out influxdb=http://localhost:8086/k6 tests/load/k6-script.js

# Import k6 dashboard in Grafana
# Dashboard ID: 2587
```

---

## Best Practices

### 1. **Start Small**
Always run smoke tests before full load tests.

### 2. **Use Realistic Data**
- Vary request parameters
- Use realistic user behavior patterns
- Include authentication flows

### 3. **Monitor Infrastructure**
Watch:
- CPU, memory, disk I/O
- Database connections
- Cache hit rates
- Network bandwidth

### 4. **Test in Stages**
Don't jump straight to maximum load. Ramp up gradually.

### 5. **Test Failure Scenarios**
- Database connection failures
- External API timeouts
- Disk space exhaustion

### 6. **Document Baselines**
Record baseline performance for comparison:
```bash
# Save results for comparison
k6 run tests/load/k6-script.js --out json=baseline-v1.0.0.json
```

### 7. **Run Regularly**
- Weekly smoke tests
- Monthly load tests
- Quarterly stress tests

---

## Troubleshooting

### High Response Times
1. Enable database query logging
2. Check for N+1 queries
3. Verify cache hit rates
4. Profile slow endpoints

### Memory Issues
1. Run soak test
2. Monitor memory over time
3. Check for connection leaks
4. Review object lifecycle

### High Error Rates
1. Check application logs
2. Verify database connection pool size
3. Check for rate limiting
4. Monitor external service health

---

## Resources

- **Locust Documentation:** https://docs.locust.io/
- **k6 Documentation:** https://k6.io/docs/
- **Load Testing Guide:** https://k6.io/blog/how-to-generate-a-constant-request-rate-with-the-new-scenarios-api/
- **Grafana Dashboards:** https://grafana.com/grafana/dashboards/?search=k6

---

## Performance Optimization Checklist

After identifying issues:

- [ ] Add database indexes
- [ ] Implement caching (Redis)
- [ ] Enable HTTP/2
- [ ] Use connection pooling
- [ ] Optimize queries (EXPLAIN ANALYZE)
- [ ] Add CDN for static assets
- [ ] Enable gzip compression
- [ ] Implement rate limiting
- [ ] Use async/await for I/O
- [ ] Scale horizontally (add replicas)
