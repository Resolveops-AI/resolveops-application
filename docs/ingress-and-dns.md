# Ingress and DNS Configuration

This document outlines the routing architecture and DNS configuration for ResolveOps AI and QuickHaul Transits.

## Architecture Overview

### ResolveOps (Kubernetes Manifests)
ResolveOps is deployed using standard Kubernetes manifests. It relies on the Azure Application Gateway Ingress Controller (AGIC) to handle traffic routing.

*   **Ingress Class**: `azure/application-gateway`
*   **Namespace**: `resolveops`
*   **Target DNS**: `resolveops-ai.sathvikdevops.online` -> **Application Gateway Public IP**

### QuickHaul (Helm/GitOps with Gateway API)
QuickHaul is deployed via GitOps/Helm. We use Kong Gateway managed via the Kubernetes Gateway API to route traffic.
*   **Gateway Class**: `kong`
*   **Namespaces**: `quickhaul-dev` and `quickhaul-prod` (with Kong deployed in `gateway-system`)
*   **Target DNS**: `quickhaul.sathvikdevops.site` -> **Kong Gateway LoadBalancer Public IP**

## DNS Records to Create

You must create the following A records (or CNAMEs) in your DNS provider:

1.  **resolveops-ai.sathvikdevops.online** -> Points to the Public IP address of the Azure Application Gateway.
2.  **quickhaul.sathvikdevops.site** -> Points to the Public IP address of the Kong LoadBalancer (in the `gateway-system` namespace).

## TLS / HTTPS
TLS configuration is currently deferred to a future implementation step and will be handled manually for now.
