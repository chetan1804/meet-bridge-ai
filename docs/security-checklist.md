# Security checklist

## Identity and access

- [ ] User authentication is required for protected routes
- [ ] JWT secrets are environment-specific and rotated regularly
- [ ] Cross-tenant checks are enforced before workspace access
- [ ] Audit logs are created for access and privileged events

## Data handling

- [ ] Uploaded artifacts are stored using secure object names and retention windows
- [ ] Sensitive documents are not logged in plaintext
- [ ] Audio retention is disabled by default unless explicitly enabled
- [ ] Deletion workflows are documented and tested

## Abuse prevention

- [ ] Rate limiting is enforced for repeated risky actions
- [ ] Monitoring and alerting are enabled for abnormal request bursts
- [ ] Invalid or malformed payloads are rejected before processing
