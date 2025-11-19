# CI/CD Workflows Documentation

This directory contains GitHub Actions workflows that automate various aspects of the RabbitRedux project, including testing, security scanning, and deployment validation.

## 📋 Workflow Overview

### 1. Main CI Pipeline (`main-ci.yml`)

**Purpose:** Primary continuous integration workflow for code quality, testing, and build validation.

**Triggers:**
- Push to `main` branch
- Pull requests targeting `main` branch

**Jobs:**
1. **Lint**: Code formatting and linting checks
   - Black formatting validation (fails on non-compliance)
   - Flake8 linting (fails on errors)
   - Pylint code quality checks
   
2. **Test**: Comprehensive testing across Python versions
   - Runs on Python 3.9, 3.10, 3.11
   - Executes pytest with coverage reporting
   - Generates HTML and XML coverage reports
   - Uploads test results as artifacts
   
3. **Build**: Application build validation
   - Validates Flask app can be created
   - Checks all imports are valid
   
4. **CI Success**: Required status check for PR merging
   - Ensures all previous jobs passed
   - Blocks PR merge if any job fails

**Artifacts Produced:**
- Test results (HTML reports)
- Coverage reports (XML and HTML)
- Retention: 30 days

---

### 2. Security Scanning (`security.yml`)

**Purpose:** Automated security vulnerability detection and analysis.

**Triggers:**
- Push to `main` branch
- Pull requests targeting `main` branch
- Scheduled daily at 2 AM UTC

**Jobs:**
1. **Dependency Scan**: Check for vulnerable dependencies
   - Safety: Known security vulnerabilities in Python packages
   - pip-audit: Python package security audit
   
2. **CodeQL Analysis**: Static Application Security Testing (SAST)
   - Analyzes Python code for security vulnerabilities
   - Security and quality queries
   - Results visible in GitHub Security tab
   
3. **Secret Scan**: Detect exposed secrets in repository
   - Gitleaks action for secret detection
   - Scans commit history for leaked credentials
   
4. **Security Summary**: Consolidated security status
   - Aggregates results from all scans
   - Provides overall security posture

**Artifacts Produced:**
- Security scan reports (JSON)
- Retention: 90 days

**Security Reports:**
- View CodeQL findings: Repository → Security → Code scanning alerts
- View Dependabot alerts: Repository → Security → Dependabot alerts

---

### 3. Docker Build & Deployment Simulation (`docker-build.yml`)

**Purpose:** Validate Docker containerization and simulate deployment workflows.

**Triggers:**
- Push to `main` branch
- Pull requests targeting `main` branch
- Manual trigger (workflow_dispatch)

**Jobs:**
1. **Docker Build Test**: Build and test Docker image
   - Uses Docker Buildx for efficient builds
   - Caches layers for faster builds
   - Tests container startup
   - Validates health endpoints
   
2. **Staging Deployment Simulation**: Simulate staging environment
   - Sets staging environment variables
   - Runs integration tests
   - Validates deployment readiness
   
3. **E2E Test**: End-to-end integration testing
   - Tests complete workflow
   - Validates production readiness

---

### 4. Dependabot Configuration (`dependabot.yml`)

**Purpose:** Automated dependency updates and security patches.

**Update Schedule:** Weekly on Mondays at 9:00 AM

**Monitored Ecosystems:**
- **Python (pip)**: Python package dependencies
- **GitHub Actions**: Workflow action versions
- **Docker**: Base image updates

**Features:**
- Groups related dependencies together
- Automatic PR creation for updates
- Labels PRs for easy identification
- Reviewer assignment

---

## 🔧 Maintenance and Updates

### Adding New Tests

1. Add test files to the `tests/` directory
2. Follow the naming convention: `test_*.py`
3. Use pytest fixtures and assertions
4. Tests will automatically run in the CI pipeline

### Updating Dependencies

Dependencies are automatically monitored by Dependabot:
- Review and merge Dependabot PRs weekly
- Test changes thoroughly before merging
- Check for breaking changes in changelogs

### Modifying Workflows

When updating workflows:
1. Test changes in a feature branch first
2. Ensure all jobs have proper error handling
3. Update this documentation if adding new workflows
4. Use `workflow_dispatch` trigger for manual testing

### Security Best Practices

- **Never commit secrets** to the repository
- Use GitHub Secrets for sensitive data
- Review security scan results regularly
- Address high/critical vulnerabilities promptly
- Keep dependencies up-to-date

---

## 🚨 Workflow Notifications

### Native GitHub Notifications

Workflows send notifications through GitHub's native system:
- **Email**: Configured in GitHub notification settings
- **Web**: Visible on pull requests and commits
- **Mobile**: GitHub mobile app notifications

### Configuring Personal Notifications

1. Go to GitHub Settings → Notifications
2. Configure email preferences
3. Enable/disable notifications for:
   - Workflow runs
   - Failed builds
   - Security alerts

---

## 📊 Viewing Workflow Results

### CI Pipeline Status

- **PR Checks**: Visible on pull request pages
- **Commit Status**: View on commit pages
- **Workflow Runs**: Actions tab in repository

### Test Results and Coverage

- Artifacts are uploaded for each workflow run
- Download from: Actions → Workflow Run → Artifacts
- Coverage trends visible in uploaded reports

### Security Findings

- **Code Scanning**: Security tab → Code scanning alerts
- **Dependabot**: Security tab → Dependabot alerts
- **Secret Scanning**: Security tab → Secret scanning alerts

---

## 🔍 Troubleshooting

### Common Issues

**Tests Failing:**
1. Check test logs in the Actions tab
2. Review coverage reports for clues
3. Run tests locally: `PYTHONPATH=. pytest tests/ -v`

**Linting Failures:**
1. Run Black locally: `black --check .`
2. Fix formatting: `black .`
3. Run Flake8: `flake8 .`

**Docker Build Failures:**
1. Check Dockerfile syntax
2. Verify base image availability
3. Test build locally: `docker build -t rabbitredux:test .`

**Security Alerts:**
1. Review the alert details
2. Check if updates are available
3. Apply patches or mitigations
4. Re-run security scans

### Getting Help

- Check workflow logs for detailed error messages
- Review this documentation
- Consult GitHub Actions documentation
- Open an issue for persistent problems

---

## 📝 Workflow Configuration Reference

### Environment Variables

All workflows use these standard environment variables:
- `GITHUB_TOKEN`: Automatically provided by GitHub
- `PYTHONPATH`: Set to repository root for imports

### Secrets Required

Optional secrets for enhanced functionality:
- `HF_TOKEN`: Hugging Face API token (for model deployment)
- `HF_USERNAME`: Hugging Face username
- `HF_PASSWORD`: Hugging Face password

### Cache Configuration

Workflows use caching for efficiency:
- Python pip cache: Speeds up dependency installation
- Docker layer cache: Reduces build times

---

## 🎯 Best Practices

### For Contributors

1. **Run tests locally** before pushing
2. **Format code** with Black before committing
3. **Check for linting errors** with Flake8
4. **Review security warnings** in PRs
5. **Keep PRs focused** and small
6. **Update tests** when adding features

### For Maintainers

1. **Review CI failures** promptly
2. **Merge Dependabot PRs** regularly
3. **Monitor security alerts** daily
4. **Update workflows** as needed
5. **Keep documentation current**
6. **Respond to workflow issues** quickly

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Docker Documentation](https://docs.docker.com/)
- [CodeQL Documentation](https://codeql.github.com/)

---

## 📅 Maintenance Schedule

- **Daily**: Security scans (automated)
- **Weekly**: Dependency updates (Dependabot)
- **Monthly**: Workflow review and optimization
- **Quarterly**: Documentation updates

---

Last Updated: 2025-11-19
Maintained by: canstralian
