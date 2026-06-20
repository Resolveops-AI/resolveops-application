# CI/CD and Security Documentation

## Architecture
The application repository (`Resolveops-AI/resolveops-application`) only utilizes **caller workflows**. All reusable CI/CD logic (Docker builds, Helm deployments, SonarQube, Snyk, Trivy scans) lives centrally in the templates repository (`Resolveops-AI/resolveops-templates`).

## Security Scans
SonarQube and Snyk scans are triggered from this repository because this repo contains the source code, Python requirements, Node package files, and Dockerfiles.
- `resolveops-ci.yml`: Scans the `frontend` and `services`
- `quickhaul-ci.yml`: Scans the `quickhaul` directory

## Dockerfile Multi-Stage Requirement
All frontend applications (Next.js, Vite/React) must implement a multi-stage `Dockerfile`. 
This guarantees that source code, `node_modules`, npm caches, and dev dependencies are excluded from the final production images, dramatically reducing image size and attack surface.

## Required GitHub Secrets
The following secrets must be configured in the application repository:
- `SONAR_TOKEN`
- `SNYK_TOKEN` (only if Snyk is enabled)
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

> **WARNING**: Do NOT add runtime application secrets as GitHub secrets (e.g., MongoDB password, Redis password, SECRET_KEY, SMTP password, Payment secret, user-entered credentials).

## Required GitHub Variables
The following variables must be configured in the application repository:
- `SONAR_PROJECT_KEY`
- `SONAR_ORGANIZATION`
- `ACR_NAME`
- `ACR_LOGIN_SERVER`
- `RESOLVEOPS_AKS_NAME`
- `RESOLVEOPS_AKS_RESOURCE_GROUP`
- `RESOLVEOPS_NAMESPACE`
- `QUICKHAUL_AKS_NAME`
- `QUICKHAUL_AKS_RESOURCE_GROUP`
- `QUICKHAUL_DEV_NAMESPACE`
- `QUICKHAUL_PROD_NAMESPACE`
