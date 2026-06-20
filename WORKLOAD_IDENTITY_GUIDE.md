# Workload Identity Guide

This project uses Azure Workload Identity to connect to Azure services without managing static credentials, and the Azure Key Vault CSI driver to securely mount secrets as files.

## Setup Flow

1. **Managed Identity**: Terraform creates a User Assigned Managed Identity.
2. **Federated Credential**: Terraform creates a Federated Identity Credential linking the Managed Identity to the Kubernetes ServiceAccount (`resolveops-workload-identity-sa`).
3. **Role Assignments**: The Managed Identity is granted necessary permissions (e.g. Key Vault Secrets User).

## Application Configuration

To use Workload Identity in a Kubernetes Deployment:

1. **ServiceAccount**: Specify the ServiceAccount created with the client-id annotation.
   ```yaml
   spec:
     serviceAccountName: resolveops-workload-identity-sa
   ```

2. **Pod Labels**: Add the Workload Identity label to the pod template so the mutating webhook injects tokens.
   ```yaml
   metadata:
     labels:
       azure.workload.identity/use: "true"
   ```

3. **Key Vault CSI Driver**: Services that need to read secrets from Key Vault use the `SecretProviderClass` and a Volume Mount. We maintain specific classes (like `azure-kvname-workload-identity-db` and `azure-kvname-workload-identity`) to control which secrets are injected (e.g. `db-password` is only provided to the API gateway and auth services).
   ```yaml
         volumeMounts:
         - name: secrets-store-inline
           mountPath: "/mnt/secrets-store"
           readOnly: true
       volumes:
       - name: secrets-store-inline
         csi:
           driver: secrets-store.csi.k8s.io
           readOnly: true
           volumeAttributes:
             secretProviderClass: "azure-kvname-workload-identity"
   ```

4. The Azure SDKs (e.g., DefaultAzureCredential in Python/Node) will automatically discover the tokens injected by the Azure Workload Identity mutating webhook and authenticate to Azure Services seamlessly.
