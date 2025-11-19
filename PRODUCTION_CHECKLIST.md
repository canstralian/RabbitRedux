# Production Deployment Checklist

Use this checklist before deploying RabbitRedux to production.

## Pre-Deployment

### Configuration
- [ ] Set strong `SECRET_KEY` environment variable (use `python -c 'import secrets; print(secrets.token_hex(32))'`)
- [ ] Set `FLASK_ENV=production`
- [ ] Configure `MODEL_NAME` if using a different model
- [ ] Set specific `CORS_ORIGINS` (not `*`)
- [ ] Review all environment variables in `.env`

### Security
- [ ] HTTPS/TLS is enabled and configured
- [ ] SSL certificates are valid and not self-signed
- [ ] Firewall rules are configured
- [ ] Only necessary ports are exposed (typically just 443 for HTTPS)
- [ ] Rate limiting is implemented (nginx or application level)
- [ ] Security headers are configured (X-Frame-Options, X-Content-Type-Options, etc.)
- [ ] Dependencies are up to date (`pip list --outdated`)
- [ ] Run security scan: `make security` or `bandit -r app/`

### Code Quality
- [ ] All tests pass: `make test`
- [ ] No linting errors: `make lint`
- [ ] Code is formatted: `make format`
- [ ] Docker image builds successfully: `make docker-build`

### Infrastructure
- [ ] Docker image is scanned for vulnerabilities: `docker scan rabbitredux:latest`
- [ ] Health check endpoint is working: `curl http://localhost:5000/health`
- [ ] Monitoring is configured
- [ ] Logging is configured and logs are being collected
- [ ] Backup strategy is in place (if needed)

### Documentation
- [ ] API documentation is up to date
- [ ] Deployment documentation matches your infrastructure
- [ ] Runbook/troubleshooting guide is available
- [ ] Team is trained on deployment procedures

## During Deployment

### Docker Deployment
```bash
# Build
make docker-build

# Tag for registry
docker tag rabbitredux:latest your-registry.com/rabbitredux:1.0.0

# Push to registry
docker push your-registry.com/rabbitredux:1.0.0

# Deploy
docker-compose up -d
```

### Smoke Tests
After deployment, run these quick checks:

1. **Health Check**
   ```bash
   curl https://your-domain.com/health
   ```
   Expected: `{"status": "healthy", "service": "RabbitRedux API"}`

2. **API Root**
   ```bash
   curl https://your-domain.com/
   ```
   Expected: Project information JSON

3. **Classification Test**
   ```bash
   curl -X POST https://your-domain.com/classify \
     -H "Content-Type: application/json" \
     -d '{"code": "def test(): pass"}'
   ```
   Expected: Classification result

4. **Error Handling**
   ```bash
   curl -X POST https://your-domain.com/classify \
     -H "Content-Type: application/json" \
     -d '{}'
   ```
   Expected: 400 error with message about missing 'code' field

## Post-Deployment

### Monitoring
- [ ] Check application logs for errors
- [ ] Verify metrics are being collected
- [ ] Set up alerts for critical errors
- [ ] Monitor resource usage (CPU, memory, disk)
- [ ] Check response times are acceptable

### Documentation
- [ ] Update deployment date in CHANGELOG.md
- [ ] Document any deployment-specific configurations
- [ ] Share deployment notes with team

### Rollback Plan
Have a rollback plan ready:
```bash
# Rollback to previous version
docker tag your-registry.com/rabbitredux:1.0.0-previous your-registry.com/rabbitredux:latest
docker-compose down
docker-compose up -d
```

## Production Maintenance

### Daily
- [ ] Check logs for errors
- [ ] Monitor performance metrics
- [ ] Verify health check endpoint

### Weekly
- [ ] Review resource usage trends
- [ ] Check for security updates: `safety check`
- [ ] Review error rates and patterns

### Monthly
- [ ] Update dependencies: `pip list --outdated`
- [ ] Run full security audit: `make security`
- [ ] Review and rotate secrets if needed
- [ ] Backup configuration and data
- [ ] Review and update documentation

### As Needed
- [ ] Scale resources based on load
- [ ] Optimize slow endpoints
- [ ] Update model if new version available
- [ ] Address security vulnerabilities immediately

## Emergency Contacts

| Role | Contact |
|------|---------|
| Primary Maintainer | [Add contact info] |
| DevOps Team | [Add contact info] |
| Security Team | [Add contact info] |

## Useful Commands

```bash
# Check application status
docker ps | grep rabbitredux

# View logs
docker logs rabbitredux -f

# Restart application
docker-compose restart

# Update and restart
git pull origin main
make docker-build
docker-compose up -d

# Run tests
make test

# Check security
make security
```

## Success Criteria

Your deployment is successful when:
- [ ] Health check returns 200 OK
- [ ] API classification requests work correctly
- [ ] Response times are < 2 seconds for typical requests
- [ ] Error rate is < 1%
- [ ] No security vulnerabilities detected
- [ ] All monitoring is active and alerting
- [ ] Team can access logs and metrics

## Notes

Add any environment-specific notes here:

- 
- 
- 
