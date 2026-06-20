# QuickHaul Transits (Sample Workload)

QuickHaul is the monitored workload application for the ResolveOps AI platform.

## Architecture & Integration

*   **ResolveOps AI** is the monitoring/AIOps platform, running in the `resolveops` namespace.
*   **QuickHaul** is the sample workload application.
*   QuickHaul will run in two AKS namespaces:
    *   `quickhaul-dev`
    *   `quickhaul-prod`
*   QuickHaul is designed to be deployed to AKS using Helm.
*   MongoDB and Redis are used inside AKS for the first version. External/AWS DB is a future optional enhancement only.
*   **Port Conflict Warning**: QuickHaul local ports `8001-8006` may conflict with ResolveOps local ports `8001-8006`.

## Deployment

A Helm chart is provided in `helm/quickhaul/` to deploy this application to AKS.
For more details, see `../docs/quickhaul-helm-aks-deployment.md`.
