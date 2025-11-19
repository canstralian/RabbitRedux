# Security Policy

## Supported Versions

Currently supported versions for security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in RabbitRedux, please report it by:

1. **Do NOT** open a public issue
2. Email the maintainer at the email address listed in the repository
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Best Practices

### For Deployment

1. **Environment Variables**
   - Never commit `.env` files with real credentials
   - Use strong, randomly generated `SECRET_KEY` in production
   - Rotate secrets regularly

2. **HTTPS/TLS**
   - Always use HTTPS in production
   - Use valid SSL/TLS certificates
   - Redirect HTTP to HTTPS

3. **CORS Configuration**
   - Set specific allowed origins instead of `*`
   - Example: `CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com`

4. **Rate Limiting**
   - Implement rate limiting at application or reverse proxy level
   - Recommended: 100 requests/minute per IP for classification endpoint
   - Lower limits for failed authentication attempts

5. **Input Validation**
   - Maximum code snippet length is enforced (10,000 characters)
   - Validate and sanitize all user inputs
   - Reject malformed requests

6. **Dependency Management**
   - Keep dependencies up to date
   - Run `pip list --outdated` regularly
   - Use `safety` to check for known vulnerabilities:
     ```bash
     pip install safety
     safety check
     ```

7. **Docker Security**
   - Run containers as non-root user (already configured)
   - Keep base images updated
   - Scan images for vulnerabilities:
     ```bash
     docker scan rabbitredux:latest
     ```

8. **Network Security**
   - Use firewalls to restrict access
   - Only expose necessary ports
   - Use VPC/private networks when possible

### For Development

1. **Code Review**
   - All changes should be reviewed before merging
   - Use pull request workflow
   - Run security linters

2. **Security Scanning**
   - Use `bandit` for Python security issues:
     ```bash
     pip install bandit
     bandit -r . -ll
     ```
   - Use `flake8` for code quality
   - Run automated security scans in CI/CD

3. **Secrets Management**
   - Never hardcode secrets
   - Use environment variables
   - Consider using secret management tools (HashiCorp Vault, AWS Secrets Manager, etc.)

4. **Logging**
   - Never log sensitive data
   - Log security-relevant events (authentication failures, etc.)
   - Implement log rotation

## Known Security Considerations

1. **Model Loading**
   - Models are loaded from Hugging Face
   - Verify model source and integrity
   - Consider using private model hosting for sensitive deployments

2. **Resource Exhaustion**
   - Large code snippets can consume significant memory
   - Input size is limited to prevent DoS
   - Consider implementing request queuing for high load

3. **Code Execution**
   - The model only classifies code, it does NOT execute it
   - Input code is treated as text only

4. **Data Privacy**
   - Code snippets sent to the API are processed in memory
   - No data is stored by default
   - Implement appropriate data retention policies if logging is enabled

## Compliance

### GDPR Considerations

If processing code from EU users:
- Implement appropriate data protection measures
- Document data processing activities
- Provide clear privacy policy
- Allow users to request data deletion

### Security Audit Trail

Recommended logging:
- Request timestamps
- IP addresses
- Response codes
- Error messages (without sensitive data)

## Security Checklist for Production

- [ ] Strong `SECRET_KEY` set via environment variable
- [ ] HTTPS/TLS enabled
- [ ] CORS configured with specific origins
- [ ] Rate limiting implemented
- [ ] Input validation in place
- [ ] Dependencies updated and scanned
- [ ] Docker image scanned for vulnerabilities
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery plan in place
- [ ] Security incident response plan documented
- [ ] Regular security audits scheduled
- [ ] Access controls and authentication implemented (if required)
- [ ] Logs are monitored and alerted on suspicious activity

## Security Updates

Security updates will be published:
- Via GitHub Security Advisories
- In release notes
- Announced in the README

Subscribe to repository notifications to stay informed.

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/stable/security/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## Contact

For security concerns, contact the maintainer through:
- GitHub: [@canstralian](https://github.com/canstralian)
- Repository Issues (for non-sensitive matters)
