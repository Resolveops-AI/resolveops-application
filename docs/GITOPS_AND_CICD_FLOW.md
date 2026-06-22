# GitOps & CI/CD Flow

This document details the CI/CD and GitOps architecture for the ResolveOps AI application, employing a FitForge-style repository setup.

## FitForge-Style Architecture
We structure our repositories to cleanly separate concerns and maximize reusability:
1. **resolveops-infrastructure**: Contains only Terraform code for infrastructure provisioning.
2. **resolveops-templates**: Contains shared, reusable GitHub Actions workflows.
3. **resolveops-application (this repo)**: Contains the application source code, Kubernetes manifests, Helm charts, and Argo CD Application manifests.

### Why not a separate charts repo?
Instead of creating a fourth repository exclusively for Helm charts and Argo CD manifests, we keep GitOps configurations alongside the application source code. This eliminates the overhead of managing a separate repository, prevents synchronization drift between code and infrastructure definitions, and simplifies the CI/CD pipeline by allowing single-commit deployments.

## The Role of Argo CD
**Argo CD is exclusively used for the QuickHaul service.**
- **QuickHaul**: Relies heavily on Kubernetes configurations (StatefulSets, PVCs, Ingress) managed via Helm and Argo CD to enforce a GitOps workflow across environments.
- **ResolveOps AI**: Because the AKS cluster is private, and ResolveOps deployments require direct management or local scripts (e.g., jumpbox/Bastion), we do not mandate Argo CD for it. ResolveOps deployments happen through direct GitHub runners (if networked) or manual `kubectl apply`.

## Branching Strategy
- **`main` is the source of truth.** All deployments stem from `main`.
- **No `dev` or `prod` branches are required.**
- Features are developed in `feature/*` branches and merged via Pull Requests.

### Why Dev/Prod Branches Are Not Needed
Environment separation happens through **Helm values overrides** rather than branch tracking. The Argo CD `quickhaul-dev` app watches `main` and applies `values-dev.yaml`. The `quickhaul-prod` app watches the same `main` branch but applies `values-prod.yaml`. This ensures that exactly the same code is promoted through environments.

## Image Versioning Strategy
One shared Azure Container Registry (ACR) stores all image versions.

- **Dev Tag Format**: `dev-<short-sha>` (e.g., `dev-a1b2c3d`)
- **Prod Tag Format**: Semantic versioning (e.g., `v1.0.0`)

### Why not use `latest`, `dev`, or `prod` tags?
Using floating tags (like `latest` or `dev`) breaks GitOps predictability because the cluster cannot guarantee which actual build is running. By using immutable tags tied to a Git commit or a semantic version release, we guarantee exact reproducibility, easier rollbacks, and clear audit trails.

## Deployment Workflows

### Dev Deployment Flow (`quickhaul-ci.yml`)
1. **Trigger**: Push to `main`.
2. **Scan**: Runs Trivy/security scans using shared templates.
3. **Build & Push**: Builds and pushes images with `dev-<short-sha>`.
4. **GitOps Update**: Automatically updates `values-dev.yaml` with the new tag and pushes the commit back to `main` with `[skip ci]`.
5. **Sync**: Argo CD automatically detects the new tag in `values-dev.yaml` and deploys to `quickhaul-dev`.

### Prod Promotion Flow (`quickhaul-promote-prod.yml`)
1. **Trigger**: Manual `workflow_dispatch`.
2. **Validation**: Ensures the semantic version tag (e.g., `v1.0.0`) does not already exist. Tags are strictly immutable.
3. **Retagging**: Pulls the verified `dev-<short-sha>` image from ACR, tags it with the semantic version, and pushes it back.
4. **GitOps Update**: Updates `values-prod.yaml` with the semantic version and commits.
5. **Sync**: Argo CD syncs to `quickhaul-prod` (either automatically or manually depending on Argo CD configuration).

### Rollback Flow
To rollback production, simply trigger the promotion workflow (or manually edit `values-prod.yaml`) to point the tag back to the previous stable semantic version. Argo CD will immediately restore the cluster state to match the declared version.

## Prerequisites

### GitHub Secrets Required
- `AZURE_CLIENT_ID`: Azure Service Principal Client ID
- `AZURE_TENANT_ID`: Azure Tenant ID
- `AZURE_SUBSCRIPTION_ID`: Azure Subscription ID
- `SONAR_TOKEN`: SonarQube token
- `SONAR_HOST_URL`: SonarQube host URL
- `SNYK_TOKEN`: Snyk security token
- `ARGOCD_AUTH_TOKEN` *(optional)*: Argo CD API token if triggering syncs from CI

### GitHub Variables Required
- `ACR_NAME`: Name of the Azure Container Registry
- `ACR_LOGIN_SERVER`: Login URL for ACR (e.g., `myacr.azurecr.io`)
- `AKS_CLUSTER_NAME`: Name of the AKS cluster
- `AZURE_RESOURCE_GROUP`: Azure Resource Group containing AKS
- `RESOLVEOPS_NAMESPACE`: Target namespace for ResolveOps AI
- `QUICKHAUL_DEV_NAMESPACE`: Target namespace for QuickHaul Dev
- `QUICKHAUL_PROD_NAMESPACE`: Target namespace for QuickHaul Prod
- `ARGOCD_SERVER` *(optional)*: FQDN of the Argo CD server
