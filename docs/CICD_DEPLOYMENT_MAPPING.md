# CI/CD Deployment Mapping Architecture

This document explains the mechanics behind how the Continuous Integration (CI) and Continuous Deployment (CD) pipelines update deployment manifests (Helm and Kustomize) in the `resolveopsai-application` repository.

## Overview

We utilize a **per-service pipeline architecture**. Each microservice has its own dedicated GitHub Actions workflow file in `.github/workflows/`. 

These workflows delegate the heavy lifting to centralized, reusable templates stored in the `resolveops-templates` repository. The CD phase specifically handles the automated updating of image tags in your Kubernetes manifests so that your CD tool (like ArgoCD) can deploy the new versions.

## The CD Template (`_cd-template.yml`)

The reusable `_cd-template.yml` is a generic manifest updater. It does not know *what* service it is deploying; instead, it relies entirely on parameters passed to it from the triggering workflow.

### Inputs Required by `_cd-template.yml`

| Parameter | Example Value | Description |
|-----------|---------------|-------------|
| `service-name` | `quickhaul-auth` | Name of the service being deployed. |
| `image-tag` | `142` (GitHub Run Number) | The new Docker image tag to deploy. |
| `environment` | `feature/dev` or `main` | Determines if this is a staging or production rollout. |
| `manifest_type` | `helm` or `kustomize` | Instructs the template on which tool to use for the update. |
| `target_dir` | `quickhaul/helm/quickhaul` | The directory containing the manifest files. |
| `update_key` | `.authService.image.tag` | The exact YAML path (for Helm) or image name (for Kustomize) to update. |

---

## How the Updates Work

### Scenario A: Helm Chart Updates (QuickHaul Services)
The 7 microservices in the `quickhaul` namespace use **Helm** for deployments. 

When a pipeline (e.g., `ci-quickhaul-auth.yml`) triggers the CD job, it passes:
- `manifest_type: helm`
- `target_dir: quickhaul/helm/quickhaul`
- `update_key: .authService.image.tag`

**Execution Logic:**
1. The CD script checks the `environment`. If `main`, it targets `values-prod.yaml`. If `feature/dev`, it targets `values-dev.yaml`.
2. It uses `yq` to perform an in-place edit of the target file:
   ```bash
   yq e ".authService.image.tag = \"142\"" -i values-dev.yaml
   ```
3. The bot commits the change directly to the repository and pushes it.

### Scenario B: Kustomize Updates (ResolveOps Core Services)
The 8 core microservices use **Kustomize** for deployments.

When a pipeline (e.g., `ci-api-gateway-service.yml`) triggers the CD job, it passes:
- `manifest_type: kustomize`
- `target_dir: kubernetes/base`
- `update_key: resolveopsacr05.azurecr.io/api-gateway-service`

**Execution Logic:**
1. The CD script changes directory to `kubernetes/base`.
2. It executes the native Kustomize command to set the new image tag:
   ```bash
   kustomize edit set image "resolveopsacr05.azurecr.io/api-gateway-service:142"
   ```
3. This modifies `kustomization.yaml` inline.
4. The bot commits `kustomization.yaml` and pushes it back to the active branch.

---

## Manual Deployment Gates

All manual deployment gates are decoupled from the code. They are enforced natively via **GitHub Environments**.

In `_cd-template.yml`, the job binds to an environment:
```yaml
jobs:
  cd:
    environment: ${{ inputs.environment }} # (e.g., 'main' or 'feature/dev')
```

Because of this binding, if you go to your Repository Settings ➔ Environments and configure "Required Reviewers" for the `main` environment, GitHub Actions will automatically **pause the workflow** right before the CD job runs. It will wait for human approval in the GitHub UI before executing the `yq`/`kustomize` logic to push the manifest update.
