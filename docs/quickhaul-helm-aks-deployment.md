# QuickHaul Helm + AKS Deployment Guide

> **QuickHaul Transits** is the sample workload application monitored by **ResolveOps AI**.
> ResolveOps AI is the AIOps/SRE monitoring platform. It is deployed independently using
> Kubernetes manifests/CI-CD — **not Helm** — and runs in its own separate AKS cluster.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Services & Ports](#services--ports)
3. [Namespaces](#namespaces)
4. [Prerequisites](#prerequisites)
5. [Helm Install Commands](#helm-install-commands)
6. [Secrets Setup](#secrets-setup)
7. [Ingress Configuration](#ingress-configuration)
8. [Argo CD Future Sync](#argo-cd-future-sync)
9. [How ResolveOps Monitors QuickHaul](#how-resolveops-monitors-quickhaul)
10. [Port Conflict Warning (Local Dev)](#port-conflict-warning-local-dev)

---

## Architecture Overview

ResolveOps AI and QuickHaul Transits run in **two separate AKS clusters** on Azure.

```
Azure
│
├── AKS Cluster: resolveops-aks
│   └── namespace: resolveops
│       └── ResolveOps AI platform
│           (deployed via Kubernetes manifests / CI-CD — NOT Helm)
│           (monitors QuickHaul as an external AKS workload)
│
└── AKS Cluster: quickhaul-aks
    ├── namespace: quickhaul-dev
    │   └── QuickHaul DEV workload (deployed via Helm)
    │       frontend, location_service, auth_service, booking_service,
    │       notification_service, otp_service, payment_service,
    │       mongodb (in-cluster), redis (in-cluster)
    │
    └── namespace: quickhaul-prod
        └── QuickHaul PROD workload (deployed via Helm)
            (same services as dev, higher replicas)
```

**Key architecture facts:**

- ResolveOps AI monitors QuickHaul as an **external** AKS workload across clusters.
- QuickHaul is deployed using **Helm** (`quickhaul/helm/quickhaul/`).
- ResolveOps is deployed independently using **Kubernetes manifests/CI-CD — not Helm**.
- MongoDB and Redis run **inside `quickhaul-aks`** for the first working/demo version.
- External AWS-hosted database connectivity is **not part of this deployment**. It can be added later as an optional hybrid-cloud enhancement.

---

## Services & Ports

All ports are **container ports** within the `quickhaul-aks` cluster. MongoDB and Redis are
`ClusterIP` services — not exposed outside the cluster.

| Service                | Container Port | Protocol | Description                         |
|------------------------|---------------|----------|-------------------------------------|
| `frontend`             | 80            | HTTP     | React/Vite frontend (Nginx)         |
| `location_service`     | 8001          | HTTP     | Location management microservice    |
| `auth_service`         | 8002          | HTTP     | Authentication microservice         |
| `booking_service`      | 8003          | HTTP     | Booking management microservice     |
| `notification_service` | 8004          | HTTP     | Notification dispatch microservice  |
| `otp_service`          | 8005          | HTTP     | OTP generation/validation           |
| `payment_service`      | 8006          | HTTP     | Payment processing microservice     |
| `mongodb`              | 27017         | TCP      | MongoDB (in-cluster, ClusterIP)     |
| `redis`                | 6379          | TCP      | Redis (in-cluster, ClusterIP)       |

---

## Namespaces

| AKS Cluster       | Namespace         | Purpose                              | Managed By                    |
|-------------------|-------------------|--------------------------------------|-------------------------------|
| `resolveops-aks`  | `resolveops`      | ResolveOps AI monitoring platform    | Kubernetes manifests / CI-CD  |
| `quickhaul-aks`   | `quickhaul-dev`   | QuickHaul DEV workload               | Helm / Argo CD                |
| `quickhaul-aks`   | `quickhaul-prod`  | QuickHaul PROD workload              | Helm / Argo CD                |

---

## Prerequisites

> ⚠️ All `kubectl` and `helm` commands below target **`quickhaul-aks`**, not `resolveops-aks`.
> Make sure your kubeconfig is pointing to `quickhaul-aks` before running any Helm command.

### 1. Set kubeconfig to `quickhaul-aks`

```bash
az aks get-credentials \
  --resource-group <quickhaul-resource-group> \
  --name quickhaul-aks \
  --overwrite-existing
```

Verify:

```bash
kubectl config current-context
# Expected output: quickhaul-aks
```

### 2. Checklist

- **`helm` v3.10+** installed
- **`kubectl`** configured to `quickhaul-aks` (see above)
- **ACR pull access** configured for `quickhaul-aks` — the recommended approach is to assign the `AcrPull` role on the AKS **kubelet managed identity**:

  ```bash
  AKS_OBJECT_ID=$(az aks show \
    --resource-group <quickhaul-resource-group> \
    --name quickhaul-aks \
    --query identityProfile.kubeletidentity.objectId -o tsv)

  az role assignment create \
    --assignee $AKS_OBJECT_ID \
    --role AcrPull \
    --scope /subscriptions/<subscription-id>/resourceGroups/<acr-resource-group>/providers/Microsoft.ContainerRegistry/registries/<acr-name>
  ```

- **Ingress controller** installed in `quickhaul-aks` if `ingress.enabled: true`
  - For NGINX: install the NGINX ingress controller Helm chart
  - For AGIC: requires Azure Application Gateway `Standard_v2` or `WAF_v2` tier and the AGIC add-on enabled on the cluster

---

## Helm Install Commands

> Make sure `kubectl` is targeting **`quickhaul-aks`** before running these commands.

### DEV

```bash
helm upgrade --install quickhaul-dev ./quickhaul/helm/quickhaul \
  -n quickhaul-dev \
  --create-namespace \
  -f ./quickhaul/helm/quickhaul/values-dev.yaml
```

### PROD

```bash
helm upgrade --install quickhaul-prod ./quickhaul/helm/quickhaul \
  -n quickhaul-prod \
  --create-namespace \
  -f ./quickhaul/helm/quickhaul/values-prod.yaml
```

### Dry-run (template preview — no cluster required)

```bash
# DEV
helm template quickhaul-dev ./quickhaul/helm/quickhaul \
  -n quickhaul-dev \
  -f ./quickhaul/helm/quickhaul/values-dev.yaml

# PROD
helm template quickhaul-prod ./quickhaul/helm/quickhaul \
  -n quickhaul-prod \
  -f ./quickhaul/helm/quickhaul/values-prod.yaml
```

### Lint

```bash
helm lint quickhaul/helm/quickhaul
```

---

## Secrets Setup

The chart does **not** create secrets automatically (to avoid committing credentials).
Create namespaces and secrets before running `helm install`.

### Step 1 — Ensure namespaces exist (idempotent)

```bash
kubectl create namespace quickhaul-dev --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace quickhaul-prod --dry-run=client -o yaml | kubectl apply -f -
```

### Step 2 — Create the secret in each namespace

The secret name must match `.Values.secretKeys` — the chart expects a secret named
`<release-name>-secrets` in the target namespace (e.g. `quickhaul-dev-secrets` for the DEV release).

> **Important:** The QuickHaul backend uses the environment variable `SECRET_KEY`
> (mapped from `shared/config.py` `secret_key` field) for JWT signing.
> Do **not** use `JWT_SECRET` — that variable does not exist in the codebase.

```bash
# DEV
kubectl create secret generic quickhaul-dev-secrets \
  --namespace quickhaul-dev \
  --from-literal=SECRET_KEY='<your-dev-secret-key>'
```

```bash
# PROD
kubectl create secret generic quickhaul-prod-secrets \
  --namespace quickhaul-prod \
  --from-literal=SECRET_KEY='<your-prod-secret-key>'
```

> **Note on MongoDB and Redis passwords:** `MONGO_PASSWORD` and `REDIS_PASSWORD` are
> **not required** for the default in-cluster demo deployment because MongoDB and Redis
> run without authentication enabled. Only add these if you explicitly enable
> authentication in `values.yaml`.

See `quickhaul/helm/quickhaul/templates/secrets.example.yaml` for the full Secret spec.

---

## Ingress Configuration

Ingress is **disabled by default** (`ingress.enabled: false` in `values.yaml`).
Enable and configure it per environment in the values override files.

### Standard NGINX

> Do not add `nginx.ingress.kubernetes.io/rewrite-target: /` unless you have intentionally
> configured path rewriting — it can break API routing for backend services.

```yaml
ingress:
  enabled: true
  className: "nginx"
  annotations: {}
  host: "quickhaul-dev.example.com"
```

### Azure Application Gateway Ingress Controller (AGIC)

> AGIC support depends on your actual cluster configuration. The Application Gateway
> must be `Standard_v2` or `WAF_v2` tier and the AGIC add-on must be enabled on `quickhaul-aks`.

```yaml
ingress:
  enabled: true
  className: "azure/application-gateway"
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    appgw.ingress.kubernetes.io/ssl-redirect: "true"
  host: "quickhaul.example.com"
  tls:
    - secretName: quickhaul-tls
      hosts:
        - quickhaul.example.com
```

---

## Argo CD Future Sync

QuickHaul is designed to be synced by Argo CD in two separate Applications — one per environment.
Argo CD should be configured to point at `quickhaul-aks` as the destination cluster.

```yaml
# Example Argo CD Application — DEV
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: quickhaul-dev
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/Resolveops-AI/resolveops-application.git
    targetRevision: HEAD
    path: quickhaul/helm/quickhaul
    helm:
      valueFiles:
        - values-dev.yaml
  destination:
    server: https://<quickhaul-aks-api-server-url>
    namespace: quickhaul-dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

```yaml
# Example Argo CD Application — PROD
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: quickhaul-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/Resolveops-AI/resolveops-application.git
    targetRevision: HEAD
    path: quickhaul/helm/quickhaul
    helm:
      valueFiles:
        - values-prod.yaml
  destination:
    server: https://<quickhaul-aks-api-server-url>
    namespace: quickhaul-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

> **Note:** Replace `<quickhaul-aks-api-server-url>` with the actual API server URL for
> `quickhaul-aks`. The Argo CD Application manifests above belong in the
> `resolveops-infrastructure` or `resolveops-templates` repo. They are shown here as
> documentation only.

---

## How ResolveOps Monitors QuickHaul

ResolveOps AI runs in the `resolveops` namespace on `resolveops-aks` and monitors
QuickHaul as an **external workload** running on `quickhaul-aks`.

### Current monitoring capability

The following is available once ResolveOps is granted access to `quickhaul-aks` via
configured RBAC and kubeconfig/service principal permissions:

- Discover QuickHaul namespaces and Kubernetes resources on `quickhaul-aks`
- Inspect pods, deployments, services, events, and logs
- Detect and analyze unhealthy pods, failed deployments, `CrashLoopBackOff`, `Pending` pods, and service availability issues

### Future enhancements (not yet implemented)

- Prometheus metrics scraping from QuickHaul pods
- `ServiceMonitor` support for cross-cluster metrics collection
- Centralized log forwarding from `quickhaul-aks` to the ResolveOps log pipeline
- Alert rules based on QuickHaul error rates, latency, and pod health
- Advanced cross-cluster AIOps correlation

---

## Port Conflict Warning (Local Dev)

> ⚠️ QuickHaul local ports `8001–8006` **may conflict** with ResolveOps local ports `8001–8006`
> when running both stacks locally via Docker Compose.
> Use `kubectl port-forward` or remap host ports in `docker-compose.yml` to avoid conflicts
> during local development.
