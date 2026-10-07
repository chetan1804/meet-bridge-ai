# Release checklist

## Pre-release

- [ ] Confirm all backend tests pass
- [ ] Confirm frontend TypeScript checks pass
- [ ] Validate environment variables for production
- [ ] Verify JWT secret is not using the default value
- [ ] Validate database and Redis connectivity in the target environment
- [ ] Confirm the app is running under the expected domain and HTTPS settings

## Security

- [ ] Review audit log coverage for sensitive operations
- [ ] Confirm tenant isolation and RBAC checks are enforced
- [ ] Validate rate limits for high-risk actions
- [ ] Review retention and deletion policies for uploaded or recorded assets

## Deployment

- [ ] Build and push Docker images
- [ ] Validate container startup commands and health checks
- [ ] Confirm secrets are stored outside source control
- [ ] Review CloudWatch / Log aggregation and error alerts

## Release signoff

- [ ] Verify core user journey with a live demo
- [ ] Capture AI evaluation metrics for the default retrieval flow
- [ ] Ensure the product README and architecture docs match the deployed version
