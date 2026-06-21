# Final Application Deployment Runbook

This runbook outlines the steps and validation checks to deploy and verify the ResolveOps AI and QuickHaul applications on the shared AKS cluster tonight.

---

## Architectural Guardrails & Final Decisions
* **No RabbitMQ**: RabbitMQ is completely removed/disabled as an active component.
* **No Kong**: Kong Gateway/Ingress is not used.
* **Ingress Integration**: Public ingress is routed exclusively via **Application Gateway WAF + AGIC Ingress**.
* **ACR Registry**: Container images are hosted on a public/accessible Azure Container Registry (ACR).
* **One Shared AKS Cluster**: Both applications run on the shared cluster `resolveops-aks-01`.
* **Database Setup**:
  * **ResolveOps AI**: Uses Azure PostgreSQL. The connection string (`DATABASE_URL`) is retrieved from Key Vault secret `database-url` synced to the cluster.
  * **QuickHaul**: Uses an in-cluster MongoDB pod with Persistent Volume claims (PVC size `2Gi` for dev, `5Gi` for prod) using the `managed-csi` StorageClass.
* **Reliability & Security**:
  * All workloads run as **non-root** users (ResolveOps uses UID/GID 10001, QuickHaul backend services use 10001, QuickHaul frontend runs Nginx on port 8080 under UID 101, MongoDB runs under UID 999).
  * Workloads include liveness/readiness probes, CPU/memory requests/limits, HorizontalPodAutoscalers (HPA), and NetworkPolicies.

---

## ResolveOps AI Deployment & Verification

Deploy the base Kustomize configuration:
```bash
# Apply ResolveOps base configuration
kubectl apply -k kubernetes/base
```

### Verification Checks:
```bash
# Check ResolveOps Pod Statuses
kubectl get pods -n resolveops

# Check ResolveOps Ingress Configuration
kubectl get ingress -n resolveops

# Check API Gateway logs for connectivity / start messages
kubectl logs deploy/api-gateway-service -n resolveops --tail=100
```

---

## QuickHaul Helm Deployment

Install/Upgrade QuickHaul in both the `dev` and `prod` namespaces:

### 1. Deploy Dev Environment:
```bash
helm upgrade --install quickhaul-dev quickhaul/helm/quickhaul \
  -n quickhaul-dev \
  -f quickhaul/helm/quickhaul/values-dev.yaml \
  --create-namespace
```

### 2. Deploy Prod Environment:
```bash
helm upgrade --install quickhaul-prod quickhaul/helm/quickhaul \
  -n quickhaul-prod \
  -f quickhaul/helm/quickhaul/values-prod.yaml \
  --create-namespace
```

### Verification Checks:
```bash
# Verify QuickHaul dev pods
kubectl get pods -n quickhaul-dev

# Verify QuickHaul prod pods
kubectl get pods -n quickhaul-prod

# Verify PVC creation and status for MongoDB dev
kubectl get pvc -n quickhaul-dev

# Verify PVC creation and status for MongoDB prod
kubectl get pvc -n quickhaul-prod

# Verify all HPAs across namespaces
kubectl get hpa -A
```
