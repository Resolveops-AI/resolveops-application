# Three-Repo Capstone Final Report

This report outlines the completion of the `resolveops-application` restructuring.

## Copied Files and Source Mapping

The application source code was successfully migrated from the original `Sathvik307393/ResolveOps-AI.git` structure into the `resolveops-application` repository.

- `original frontend/` → `resolveops-application/frontend/`
- `original services/api-gateway-service/` → `resolveops-application/services/api-gateway-service/`
- `original services/auth-service/` → `resolveops-application/services/auth-service/`
- `original services/github-intelligence-service/` → `resolveops-application/services/github-intelligence-service/`
- `original services/azure-intelligence-service/` → `resolveops-application/services/azure-intelligence-service/`
- `original services/aws-intelligence-service/` → `resolveops-application/services/aws-intelligence-service/`
- `original services/ai-rca-service/` → `resolveops-application/services/ai-rca-service/`
- `original services/notification-service/` → `resolveops-application/services/notification-service/`

**Note on unused code**: The `services/shared/` directory from the original repository was not copied, as it is composed of unused stubs not imported by any of the active services.

## Kubernetes Manifests

Kubernetes manifests were successfully generated inside `resolveops-application/kubernetes/`:
- `namespace.yaml`
- `configmap.yaml`
- `serviceaccount.yaml`
- `secretproviderclass.yaml`
- Deployment and Service definitions for all 8 microservices
- `ingress.yaml`
- `kustomization.yaml`

Key Vault integration uses the `SecretProviderClass` injected via CSI driver to securely mount secrets as volumes, avoiding the need for a hardcoded `secrets.yaml`.

## Docker Build Contexts

Dockerfiles are retained in each service. The build context expected for all backend services is the service's specific directory (e.g., `./services/api-gateway-service`), while the frontend is built from `./frontend`. A `docker-compose.yml` was generated in the root directory to facilitate local development testing.

## Workflow Behavior

The GitHub Action (`.github/workflows/build-deploy.yml`) is designed to:
1. Trigger on push to `main` and manually.
2. Run in a build matrix for all services.
3. Perform required security scans (SonarQube, Snyk, Trivy) without bypassing errors.
4. Build Docker images and push them to ACR using Azure OIDC.
5. Deploy to AKS using Kustomize (`kubectl apply -k kubernetes/`), updating images dynamically to the GitHub SHA tag.

## Key Vault Secret Strategy

Secrets are not committed into version control. Instead, a `secretproviderclass.yaml` connects to Azure Key Vault to dynamically fetch sensitive items like `jwt-secret`, `smtp-user`, `smtp-password`, `ai-provider-api-key`, etc. The CSI driver maps these Key Vault secrets as volumes inside the pods using Workload Identity.

## Workload Identity Flow

Azure Workload Identity eliminates the need for managing service principals and static secrets:
- The ServiceAccount `resolveops-workload-identity-sa` is annotated with the Azure Client ID.
- Deployments accessing Azure services (e.g., `api-gateway-service`, `azure-intelligence-service`, `ai-rca-service`) reference this ServiceAccount and use the label `azure.workload.identity/use: "true"`.
- Azure AD issues short-lived tokens to the pods based on the federated identity credential.

## Validation Commands

Run these to verify local structure:
```bash
ls resolveops-application/frontend
ls resolveops-application/services
ls resolveops-application/kubernetes
```

Run these to verify Kubernetes manifests locally (requires `kubectl`):
```bash
kubectl apply -k resolveops-application/kubernetes/ --dry-run=client
```

After deployment to AKS, run these commands to ensure health:
```bash
kubectl get pods -n resolveops-dev
kubectl get svc -n resolveops-dev
kubectl get ingress -n resolveops-dev
```

## Remaining Manual Setup Steps

1. Configure GitHub variables (`ACR_NAME`, `ACR_LOGIN_SERVER`, `AZURE_RESOURCE_GROUP`, `AKS_CLUSTER_NAME`, `AKS_NAMESPACE`, `WORKLOAD_IDENTITY_CLIENT_ID`, `KEY_VAULT_NAME`) and secrets (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `SONAR_TOKEN`, `SONAR_HOST_URL`, `SNYK_TOKEN`).
2. Provision Azure Infrastructure via Terraform (this establishes the AKS cluster, ACR, Key Vault, and Managed Identity).
3. Populate the Azure Key Vault with the real values for secrets like `jwt-secret`.
4. Trigger the GitHub Action to execute the first deployment.
