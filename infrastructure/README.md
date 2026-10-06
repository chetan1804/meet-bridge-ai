# Infrastructure

This directory is reserved for deployment, environment, and operational configuration assets for the v1.0.0 release.

## Recommended AWS deployment architecture

- Frontend: AWS ALB + ECS Fargate or EKS deployment for the Next.js app
- Backend: private ECS Fargate or EKS service behind the ALB
- Database: Amazon RDS PostgreSQL in private subnets
- Caching and session state: Amazon ElastiCache Redis
- Secure file storage: S3 with lifecycle rules and encryption at rest
- Secrets: AWS Secrets Manager for JWT keys, database credentials, and provider tokens
- Observability: CloudWatch Logs, metrics, and alarms

## Operational guidance

- Keep the app behind HTTPS only
- Use private subnets for database and Redis
- Restrict inbound access to the ALB and required management paths
- Configure automated backups and lifecycle rules for retention
- Read the project checklists in [../docs/release-checklist.md](../docs/release-checklist.md) and [../docs/security-checklist.md](../docs/security-checklist.md)

## Production assumptions

- environment is set to production
- secrets are injected from the deployment environment, not committed to source control
- container health checks pass before deployment completes
- release verification includes backend tests and frontend type-checking
