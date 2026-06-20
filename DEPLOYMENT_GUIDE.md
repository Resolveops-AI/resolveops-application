# Deployment Guide

This guide details how to deploy the ResolveOps application to Azure Kubernetes Service (AKS) using environment-based Kustomize overlays.

## Prerequisites

- Active AKS Cluster
- Azure Container Registry (ACR)
- Azure Key Vault with Secrets Configured
- GitHub repository secrets and variables configured

## GitHub Actions Variables and Secrets

The primary deployment mechanism is the `build-deploy.yml` workflow.

### Required GitHub Secrets:
- `AZURE_CLIENT_ID`: The Client ID for OIDC federation.
- `AZURE_TENANT_ID`: The Tenant ID of the Azure AD. (can also be a variable).
- `AZURE_SUBSCRIPTION_ID`: Azure Subscription ID.
- `SONAR_TOKEN`, `SONAR_HOST_URL`: For SonarQube static analysis.
- `SNYK_TOKEN`: For Snyk dependency scanning.

### Required GitHub Variables:
- `ACR_NAME`: e.g., `myacr`
- `ACR_LOGIN_SERVER`: e.g., `myacr.azurecr.io`
- `AZURE_RESOURCE_GROUP`: e.g., `rg-resolveops`
- `AKS_CLUSTER_NAME`: e.g., `aks-resolveops`
- `AKS_NAMESPACE`: (Default: `resolveops-dev`)
- `WORKLOAD_IDENTITY_CLIENT_ID`: Used in Kustomize manifests.
- `KEY_VAULT_NAME`: Used in SecretProviderClass.
- `AZURE_TENANT_ID`: Used in SecretProviderClass.

### Mapping from Terraform Outputs:
The Terraform infrastructure repository outputs these exact values. Map the Terraform outputs directly to the corresponding GitHub Secret or Variable.

## Private AKS Note

**IMPORTANT**: If your AKS cluster is deployed as a Private Cluster, the GitHub Actions workflow will fail to reach the Kubernetes API. You must run the deployment workflow on a self-hosted GitHub runner deployed inside the AKS VNet.

## Validation Commands

To validate the Kustomize rendering locally:
```bash
kubectl kustomize kubernetes/overlays/dev
```

To dry-run against the cluster (requires AKS credentials):
```bash
kubectl kustomize kubernetes/overlays/dev | envsubst | kubectl apply -f - --dry-run=client
```

To verify the deployment in the cluster:
```bash
kubectl get pods -n resolveops-dev
kubectl get svc -n resolveops-dev
kubectl get ingress -n resolveops-dev
```
