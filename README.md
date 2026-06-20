# ResolveOps AI - Application

This repository contains the application source code and Kubernetes deployment manifests for ResolveOps AI.

## Architecture

The system consists of the following microservices:
- `frontend`: Next.js web interface
- `api-gateway-service`: Main entrypoint for backend APIs
- `auth-service`: Authentication and authorization
- `github-intelligence-service`: GitHub integration and intelligence
- `azure-intelligence-service`: Azure integration and insights
- `aws-intelligence-service`: AWS integration and insights
- `ai-rca-service`: AI-powered Root Cause Analysis
- `notification-service`: Email and alerting system

## Local Development

You can run the entire application stack locally using `docker-compose`.

```bash
# 1. Copy the environment variables example
cp .env.example .env

# 2. Build and run containers
docker-compose up --build
```

Access the frontend at `http://localhost:3000` and the API Gateway at `http://localhost:8000`.

## CI/CD and Deployment

Deployment to Azure Kubernetes Service (AKS) is automated via GitHub Actions (`.github/workflows/build-deploy.yml`). 
See `DEPLOYMENT_GUIDE.md` for more details.
