# Workload Identity Guide

This project uses Azure Workload Identity to connect to Azure services without managing static credentials.

## Setup Flow

1. **Managed Identity**: Terraform creates a User Assigned Managed Identity.
2. **Federated Credential**: Terraform creates a Federated Identity Credential linking the Managed Identity to the Kubernetes ServiceAccount (`resolveops-workload-identity-sa`).
3. **Role Assignments**: The Managed Identity is granted necessary permissions (e.g. Key Vault Secrets User).

## Application Configuration

To use Workload Identity in a Kubernetes Deployment:

1. Specify the ServiceAccount:
   ```yaml
   spec:
     serviceAccountName: resolveops-workload-identity-sa
   ```

2. Add the Workload Identity label to the pod template:
   ```yaml
   metadata:
     labels:
       azure.workload.identity/use: "true"
   ```

3. The Azure SDKs (e.g., DefaultAzureCredential in Python/Node) will automatically discover the tokens injected by the Azure Workload Identity mutating webhook and authenticate to Azure Services seamlessly.
