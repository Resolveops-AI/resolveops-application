# Deployment Guide

This guide details how to deploy the ResolveOps application to Azure Kubernetes Service (AKS).

## Prerequisites

- Active AKS Cluster
- Azure Container Registry (ACR)
- GitHub repository secrets and variables configured

## GitHub Actions

The primary deployment mechanism is the `build-deploy.yml` workflow.

It requires the following secrets:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `SONAR_TOKEN`
- `SONAR_HOST_URL`
- `SNYK_TOKEN`

And the following variables:
- `ACR_NAME`
- `ACR_LOGIN_SERVER`
- `AZURE_RESOURCE_GROUP`
- `AKS_CLUSTER_NAME`
- `AKS_NAMESPACE`
- `WORKLOAD_IDENTITY_CLIENT_ID`
- `KEY_VAULT_NAME`

## Private AKS Note

**IMPORTANT**: If your AKS cluster is deployed as a Private Cluster, the GitHub Actions workflow will fail to reach the Kubernetes API. You must run the deployment workflow on a self-hosted GitHub runner deployed inside the AKS VNet.

## Manual Deployment

To manually apply the manifests:

```bash
# 1. Get AKS credentials
az aks get-credentials --resource-group <resource_group> --name <cluster_name>

# 2. Apply kustomize
kubectl apply -k kubernetes/
```
