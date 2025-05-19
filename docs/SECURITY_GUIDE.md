# Security Guide for BetterRepo2File v2.0

This guide outlines security best practices for deploying and operating BetterRepo2File v2.0 in production environments.

## Environment Configuration

### 1. Environment Variables

Always use the `.env` file for sensitive configuration:

```bash
# Copy the example file
cp .env.example .env

# Edit with secure values
nano .env
```

**Required Security Changes:**
- `SECRET_KEY`: Generate a secure random string (32+ characters)
- `REDIS_PASSWORD`: Set a strong password for Redis
- `MINIO_ACCESS_KEY` & `MINIO_SECRET_KEY`: Change from defaults
- `SESSION_COOKIE_SECURE`: Set to `true` for HTTPS environments

### 2. Generating Secure Keys

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate secure passwords
openssl rand -base64 32
```

## Docker Security

### 1. Network Isolation

The Docker Compose setup creates an isolated network for services. In production:

```yaml
# docker-compose.prod.yml
services:
  redis:
    expose:
      - "6379"  # Remove external port mapping
    # Don't use "ports" in production
    
  minio:
    expose:
      - "9000"  # Internal only
    ports:
      - "127.0.0.1:9001:9001"  # Console on localhost only
```

### 2. Docker Secrets (Production)

For production deployments, use Docker secrets:

```yaml
# docker-compose.prod.yml
secrets:
  redis_password:
    file: ./secrets/redis_password.txt
  minio_access_key:
    file: ./secrets/minio_access_key.txt
  minio_secret_key:
    file: ./secrets/minio_secret_key.txt

services:
  redis:
    command: redis-server --appendonly yes --requirepass_file /run/secrets/redis_password
    secrets:
      - redis_password
```

## Redis Security

### 1. Authentication

Always set a password for Redis:

```bash
# In .env
REDIS_PASSWORD=your-secure-password-here
```

### 2. Configuration

Additional Redis security settings:

```conf
# redis.conf
requirepass your-secure-password
bind 127.0.0.1 ::1  # Only listen on localhost
protected-mode yes
```

### 3. Network Access

- Never expose Redis port 6379 to the internet
- Use firewall rules to restrict access
- Consider using Redis ACLs for fine-grained permissions

## MinIO Security

### 1. Access Keys

Change default credentials immediately:

```bash
# In .env
MINIO_ACCESS_KEY=your-secure-access-key
MINIO_SECRET_KEY=your-secure-secret-key
```

### 2. Bucket Policies

Implement least-privilege bucket policies:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["arn:aws:iam::*:user/app-user"]},
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": ["arn:aws:s3:::betterrepo2file/*"]
    }
  ]
}
```

### 3. Encryption

Enable server-side encryption:

```bash
# Start MinIO with encryption
docker run -p 9000:9000 minio/minio server /data \
  --certs-dir /certs \
  --encrypt
```

## Flask Application Security

### 1. Session Security

Configure secure sessions in production:

```python
# app/config.py - ProductionConfig
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JS access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

### 2. Security Headers

Implement security headers:

```python
# app/app.py
from flask_talisman import Talisman

if app.config['ENV'] == 'production':
    Talisman(app, force_https=True)
```

### 3. Input Validation

Always validate user inputs:

```python
# Example validation
if not repo_url.startswith('https://github.com/'):
    raise ValueError("Invalid repository URL")
```

## Celery Security

### 1. Message Signing

Enable message signing in Celery:

```python
# app/celery_app.py
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    event_serializer='json',
    task_protocol=2,
    worker_hijack_root_logger=False,
    worker_log_color=False
)
```

### 2. Result Backend Security

Secure the result backend:

```python
# Use separate Redis database for results
CELERY_RESULT_BACKEND = 'redis://:password@localhost:6379/1'
```

## Network Security

### 1. Firewall Rules

Implement strict firewall rules:

```bash
# Allow only necessary ports
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP (redirect to HTTPS)
ufw allow 443/tcp  # HTTPS
ufw enable
```

### 2. TLS/SSL Configuration

Always use HTTPS in production:

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
}
```

## Monitoring and Auditing

### 1. Log Sensitive Operations

Log all security-relevant events:

```python
logger.info(f"User {user_id} accessed repository {repo_url}")
logger.warning(f"Failed authentication attempt from {ip_address}")
```

### 2. Monitor Access Patterns

Set up alerts for suspicious activity:

- Multiple failed authentication attempts
- Unusual data access patterns
- Large file uploads/downloads

### 3. Regular Security Audits

- Review access logs monthly
- Update dependencies regularly
- Perform security scans

## Deployment Checklist

Before deploying to production:

- [ ] Changed all default passwords
- [ ] Set `SESSION_COOKIE_SECURE=true`
- [ ] Configured HTTPS/TLS
- [ ] Restricted network access to services
- [ ] Enabled logging and monitoring
- [ ] Set up backup procedures
- [ ] Tested disaster recovery plan
- [ ] Reviewed and applied security headers
- [ ] Validated all input handling
- [ ] Updated all dependencies to latest secure versions

## Incident Response

In case of security incidents:

1. **Isolate**: Disconnect affected systems
2. **Assess**: Determine scope of breach
3. **Contain**: Stop further damage
4. **Eradicate**: Remove threat
5. **Recover**: Restore from secure backups
6. **Learn**: Update procedures

## Regular Maintenance

### Weekly
- Review access logs
- Check for security updates

### Monthly
- Update dependencies
- Review user access
- Test backups

### Quarterly
- Security audit
- Penetration testing
- Update security procedures

## Resources

- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Flask Security Guide](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Redis Security](https://redis.io/topics/security)
- [MinIO Security](https://docs.min.io/docs/minio-security-overview.html)

Remember: Security is an ongoing process, not a one-time setup.