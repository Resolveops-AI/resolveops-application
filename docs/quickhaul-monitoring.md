# QuickHaul GitOps and Monitoring

This document outlines the GitOps and monitoring deployment for the QuickHaul application.

## Architecture and Responsibilities

It is important to distinguish the different responsibilities in this architecture:

* **Infrastructure (Terraform & AKS):** Terraform creates the `quickhaul-aks` cluster and provisions the core namespaces (`argocd`, `monitoring`, `quickhaul-dev`, `quickhaul-prod`). The application repository does not permanently manage namespace creation.
* **GitOps (Argo CD):** Argo CD is installed in the `argocd` namespace and manages the declarative deployment of QuickHaul to the dev and prod namespaces, as well as deploying the monitoring stack.
* **Monitoring (Prometheus & Grafana):** Installed in the `monitoring` namespace, responsible for gathering metrics and serving dashboards.
* **ResolveOps AI:** A completely independent application running in the `resolveops-aks` cluster, which evaluates data and provides AI-based analysis (and will consume monitoring data in the future).

## Monitoring Scope

> [!NOTE]
> QuickHaul currently does not expose Prometheus `/metrics` endpoints. 
> The current implementation monitors **Kubernetes metrics only**. 

Monitored metrics include:
* Pod status and readiness
* Restart count (CrashLoopBackOff, frequent restarts)
* Deployment availability (including Redis and MongoDB)
* CPU and Memory usage

Application-level metrics can be enabled later by uncommenting the ServiceMonitor in `gitops/monitoring/quickhaul-servicemonitor.yaml` once the application exposes a `/metrics` endpoint.

## Installation

### 1. Install Argo CD (Manual Fallback)

Argo CD must first be installed in the `argocd` namespace. If it is not already installed via infrastructure automation, you can install it manually:

```bash
kubectl create namespace argocd

helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

helm upgrade --install argocd argo/argo-cd -n argocd
```

### 2. Prepare Grafana Credentials

Grafana credentials must never be hardcoded. Before deploying the monitoring stack, create a generic secret containing the desired admin credentials in the `monitoring` namespace (ensure the namespace exists first):

```bash
# Create monitoring namespace if it doesn't exist
kubectl create namespace monitoring

kubectl create secret generic grafana-admin-secret \
  -n monitoring \
  --from-literal=admin-user=admin \
  --from-literal=admin-password='<your-password>'
```

### 3. Deploy GitOps Applications

Apply the Argo CD manifests to instruct Argo CD to deploy QuickHaul and the Monitoring stack:

```bash
kubectl apply -f gitops/argocd/monitoring.yaml
kubectl apply -f gitops/argocd/quickhaul-dev.yaml
kubectl apply -f gitops/argocd/quickhaul-prod.yaml
```

*Note: If Argo CD fails to deploy the `kube-prometheus-stack` via multiple sources, you may fall back to manual Helm installation using the provided values file (`helm upgrade --install prometheus prometheus-community/kube-prometheus-stack -n monitoring -f gitops/monitoring/values-kube-prometheus-stack.yaml`).*

### 4. Accessing Grafana

Once the monitoring stack is fully deployed, you can access Grafana using port-forwarding:

```bash
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-grafana 3000:80
```

Log in using the credentials you defined in the `grafana-admin-secret`.

## Prometheus Alerts

The following alerts are configured exclusively for the `quickhaul-dev` and `quickhaul-prod` namespaces to avoid cluster-wide noise:
* `QuickHaulCrashLoopBackOff`
* `QuickHaulFrequentPodRestarts`
* `QuickHaulDeploymentUnavailable`
* `QuickHaulPodNotReady`
* `QuickHaulHighCPU`
* `QuickHaulHighMemory`
* `QuickHaulMongoDbUnavailable`
* `QuickHaulRedisUnavailable`
