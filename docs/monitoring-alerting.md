# Monitoring and Alerting: Better Auth Integration

This document outlines the monitoring and alerting strategy for the Better Auth authentication system.

## Overview

The monitoring and alerting system tracks authentication metrics to ensure system reliability, security, and performance. This includes monitoring authentication success/failure rates, token validation, and security events.

## Key Metrics to Monitor

### 1. Authentication Metrics

#### Login Success/Failure Rates
- **Metric**: `auth.login.success.count`, `auth.login.failure.count`
- **Purpose**: Track successful vs failed login attempts
- **Alert Threshold**: >10% failure rate over 5 minutes

#### Registration Success/Failure Rates
- **Metric**: `auth.registration.success.count`, `auth.registration.failure.count`
- **Purpose**: Track successful vs failed registration attempts
- **Alert Threshold**: >10% failure rate over 5 minutes

#### Token Validation Rates
- **Metric**: `auth.token.validation.success.count`, `auth.token.validation.failure.count`
- **Purpose**: Track token validation success/failure
- **Alert Threshold**: >5% failure rate over 5 minutes

### 2. Performance Metrics

#### Authentication Response Times
- **Metric**: `auth.response.time.ms`
- **Purpose**: Track response time for authentication endpoints
- **Alert Threshold**: >1000ms p95 response time

#### Token Validation Performance
- **Metric**: `auth.token.validation.time.ms`
- **Purpose**: Track JWT validation performance
- **Alert Threshold**: >100ms average validation time

### 3. Security Metrics

#### Failed Authentication Attempts
- **Metric**: `auth.login.failure.count`
- **Purpose**: Track failed login attempts (potential brute force)
- **Alert Threshold**: >50 failures from same IP in 10 minutes

#### Rate Limiting Events
- **Metric**: `auth.rate.limit.exceeded.count`
- **Purpose**: Track when rate limits are hit
- **Alert Threshold**: >10 rate limit events in 1 minute

#### Invalid Token Attempts
- **Metric**: `auth.invalid.token.attempts.count`
- **Purpose**: Track attempts with invalid/expired tokens
- **Alert Threshold**: Sudden spike (>200%) in invalid token attempts

## Implementation Strategy

### 1. Application-Level Logging

The application should log authentication events using the `LoginAuditLogger`:

```python
from backend.src.auth.login_logger import get_login_audit_logger

audit_logger = get_login_audit_logger()

# Log successful login
audit_logger.log_login_success(user_id, ip_address, user_agent)

# Log failed login
audit_logger.log_login_failure(user_id, ip_address, user_agent, "Invalid credentials")

# Log token events
audit_logger.log_token_issued(user_id, "access", ip_address, user_agent)
```

### 2. Metrics Collection

#### Using Prometheus/Grafana
```python
from prometheus_client import Counter, Histogram, Gauge

# Define counters
login_success_counter = Counter('auth_login_success_total', 'Successful logins')
login_failure_counter = Counter('auth_login_failure_total', 'Failed logins')
token_validation_counter = Counter('auth_token_validation_total', 'Token validation attempts')

# Define histograms for timing
auth_response_time = Histogram('auth_response_time_seconds', 'Authentication response time')
token_validation_time = Histogram('auth_token_validation_time_seconds', 'Token validation time')
```

### 3. Health Checks

#### Authentication Service Health
- **Endpoint**: `/auth/health`
- **Purpose**: Verify authentication service is operational
- **Metrics**: Response time, availability

#### Database Connection Health
- **Purpose**: Verify user database is accessible
- **Metrics**: Connection pool status, query response times

## Alert Configuration

### 1. Critical Alerts

#### Authentication Service Down
- **Condition**: `/auth/health` endpoint returns error for >2 consecutive checks
- **Severity**: Critical
- **Notification**: Page on-call engineer immediately

#### High Authentication Failure Rate
- **Condition**: >20% login failure rate over 5 minutes
- **Severity**: Critical
- **Notification**: Slack channel + email

#### Rate Limiting Under Attack
- **Condition**: >100 rate limit events in 1 minute
- **Severity**: Warning/Critical based on volume
- **Notification**: Slack channel

### 2. Warning Alerts

#### Elevated Response Times
- **Condition**: p95 response time >500ms for authentication endpoints
- **Severity**: Warning
- **Notification**: Slack channel

#### Sudden Spike in Registrations
- **Condition**: 5x increase in registration rate over 10 minutes
- **Severity**: Warning
- **Notification**: Email

#### Token Validation Performance Degradation
- **Condition**: Average token validation time >50ms
- **Severity**: Warning
- **Notification**: Email

## Dashboard Requirements

### 1. Authentication Dashboard
- Login success/failure rates over time
- Registration success/failure rates
- Token validation rates
- Response time percentiles
- Active sessions/users

### 2. Security Dashboard
- Failed authentication attempts by IP
- Rate limiting events
- Invalid token attempts
- User lockout events
- Geographic distribution of auth attempts

### 3. Performance Dashboard
- Authentication endpoint response times
- Token validation performance
- Database query performance
- System resource utilization

## Log Retention Policy

### 1. Authentication Logs
- **Retention**: 90 days
- **Storage**: Secure, encrypted storage
- **Access**: Limited to authorized personnel only

### 2. Security Events
- **Retention**: 1 year
- **Storage**: Immutable storage for compliance
- **Access**: Auditing required for access

## Incident Response

### 1. Authentication Service Failure
1. Check application logs for error details
2. Verify database connectivity
3. Check environment variables (secrets)
4. Restart service if necessary
5. Notify stakeholders

### 2. Security Incident (Brute Force Attack)
1. Identify source IPs of attack
2. Temporarily block malicious IPs at firewall level
3. Increase rate limiting thresholds temporarily
4. Notify security team
5. Document incident for future prevention

### 3. Performance Degradation
1. Check system resource utilization
2. Analyze slow query logs
3. Scale application resources if needed
4. Optimize database queries
5. Review authentication logic for inefficiencies

## Best Practices

### 1. Secure Metric Collection
- Don't include sensitive data in metrics
- Use secure connections for metric transmission
- Limit access to metric dashboards

### 2. Regular Review
- Review authentication metrics weekly
- Update alert thresholds based on traffic patterns
- Audit access to monitoring systems monthly

### 3. Documentation
- Document all alert conditions and responses
- Maintain runbooks for common incidents
- Update metrics documentation as system evolves

## Tools and Technologies

### 1. Recommended Stack
- **Metrics**: Prometheus for collection, Grafana for visualization
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana) or similar
- **Alerting**: Alertmanager (with Prometheus) or commercial solution
- **APM**: Application Performance Monitoring tool for detailed tracing

### 2. Integration Points
- Application logging integrated with audit logger
- Metrics exposed via `/metrics` endpoint
- Health checks available at `/health` endpoints
- Structured logging for easy parsing