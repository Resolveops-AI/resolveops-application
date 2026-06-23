# AKS Node Pool Scheduling

This document describes the AKS node pool layout for this project and how application workloads are directed to the correct pool.

---

## Node Pool Architecture

The AKS cluster is provisioned with **two node pools**:

| Pool | Name | Purpose |
|------|------|---------|
| System pool | `systempool` | AKS/Kubernetes system components (kube-dns, metrics-server, AGIC, CSI drivers, etc.) |
| User pool | `userpool` | All application workloads (ResolveOps AI, QuickHaul, monitoring) |

### Labels

User pool nodes carry the AKS-managed label:

```
kubernetes.azure.com/mode=user
```

### Taints

The system pool is (or will be) protected by:

```
CriticalAddonsOnly=true:NoSchedule
```

This taint prevents non-system pods from landing on the system pool. Only pods with the matching toleration (`CriticalAddonsOnly`) can schedule there.

> **Note:** Some AKS-managed DaemonSets (e.g., `azure-npm`, `csi-azuredisk-node`, `kube-proxy`) carry a `CriticalAddonsOnly` toleration by design and will run on **all** nodes. This is expected AKS behaviour.

---

## How Application Pods Are Scheduled

All application Deployments and StatefulSets include a `nodeSelector` that targets the user node pool:

```yaml
spec:
  template:
    spec:
      nodeSelector:
        kubernetes.azure.com/mode: user
```

### ResolveOps AI — `kubernetes/base/`

The following Deployment manifests have been updated:

| Manifest | Deployment |
|----------|-----------|
| `frontend.yaml` | `frontend` |
| `api-gateway-service.yaml` | `api-gateway-service` |
| `auth-service.yaml` | `auth-service` |
| `github-intelligence-service.yaml` | `github-intelligence-service` |
| `azure-intelligence-service.yaml` | `azure-intelligence-service` |
| `aws-intelligence-service.yaml` | `aws-intelligence-service` |
| `ai-rca-service.yaml` | `ai-rca-service` |
| `notification-service.yaml` | `notification-service` |

### QuickHaul — `quickhaul/helm/quickhaul/`

The `nodeSelector` is defined once in `values.yaml`:

```yaml
nodeSelector:
  kubernetes.azure.com/mode: user
```

And rendered in every template via:

```yaml
nodeSelector:
  {{- toYaml .Values.nodeSelector | nindent 8 }}
```

Templates updated:

| Template | Kind |
|----------|------|
| `templates/deployment.yaml` (frontend section) | Deployment |
| `templates/deployment.yaml` (backend services loop) | Deployment × 6 |
| `templates/mongodb-statefulset.yaml` | StatefulSet |

Backend services included in the loop: `locationService`, `authService`, `bookingService`, `notificationService`, `otpService`, `paymentService`.

### Monitoring — `gitops/monitoring/values-kube-prometheus-stack.yaml`

`nodeSelector: kubernetes.azure.com/mode: user` has been added under:
- `grafana`
- `prometheus.prometheusSpec`

This ensures Prometheus and Grafana pods run on the user pool.

---

## Argo CD

Argo CD was installed **manually from upstream manifests** and is **not managed by Helm values in this repo**.

> **Action Required (future):** When Argo CD is brought under Helm/GitOps management, add `nodeSelector: kubernetes.azure.com/mode: user` to its Deployment / StatefulSet specs so it also runs on the user pool. Until then, verify placement manually.

The Argo CD Application manifests in `quickhaul/argocd/` and `gitops/argocd/` are sync definitions only and do not control Argo CD's own scheduling.

---

## Verification Commands

After deploying, run the following to confirm pod placement:

```bash
# Inspect node labels — confirm userpool nodes are labelled correctly
kubectl get nodes -L kubernetes.azure.com/mode

# Broad view: all pods and the nodes they landed on
kubectl get pods -A -o wide

# ResolveOps AI pods
kubectl get pods -n resolveops-ai -o wide

# QuickHaul dev pods
kubectl get pods -n quickhaul-dev -o wide

# QuickHaul prod pods
kubectl get pods -n quickhaul-prod -o wide
```

All application pods should show a node in the `userpool` (mode=user) column.

---

## Troubleshooting

If a pod is stuck in `Pending` after these changes:

1. Run `kubectl describe pod <pod-name> -n <namespace>` and check `Events`.
2. A `0/N nodes are available: N node(s) didn't match Pod's node affinity/selector` message means the node label is not present.
3. Verify the node pool label with `kubectl get nodes --show-labels | grep kubernetes.azure.com/mode`.
