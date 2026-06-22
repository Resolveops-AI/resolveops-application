# GitOps and CI/CD Flow

This document details the CI/CD execution flow mapping from code commit to Kubernetes deployment via Argo CD.

## 1. Push to `dev`
- **Validation**: Runs lint testing, SAST, Snyk, and Helm validation.
- **Image Build**: Docker dev images are built locally.
- **Security Scan**: `aquasecurity/trivy-action` scans the newly built images. Fails the workflow if `HIGH` or `CRITICAL` vulnerabilities exist.
- **Image Push**: If the scan passes, images are pushed to ACR with the tag format: `dev-<short-sha>`.
- **GitOps Commit**: ONLY AFTER the images are successfully pushed, the `quickhaul/helm/quickhaul/values-dev.yaml` file is updated with the new `dev-<short-sha>` tag. The GitHub Action commits this change back to the source branch (`dev`) using `[skip ci]`.
- **Argo CD Dev Deployment**: Argo CD's `quickhaul-dev` Application is configured with `targetRevision: dev`. When the bot commits to `dev`, Argo CD detects the updated `values-dev.yaml` and deploys the new images to the `quickhaul-dev` namespace in the AKS cluster.

## 2. Pull Request (`dev` → `main`)
When a PR is opened targeting `main`:
- **Validation**: Runs lint testing, SAST, Snyk, and Helm validation to ensure code quality before merging.
- **Images**: No images are built.
- **Registry**: No ACR pushes occur.
- **Helm**: No updates to `values-dev.yaml`.
- **Deployment**: No deployment changes happen.

## 3. Merge to `main`
When the PR is approved and merged:
- **Secondary Validation**: Lint testing, SAST, Snyk, and Helm validation run again.
- **Semantic Versioning**: `github-tag-action` analyzes Conventional Commits to determine the new `vX.Y.Z` version tag.
- **Tag Check**: Validates that `vX.Y.Z` does not already exist in ACR.
- **Promotion Prep**: Reads the tested `dev-<short-sha>` tag from `values-dev.yaml` and pulls the image from ACR.
- **Candidate Scan**: Trivy scans the dev image again to ensure no newly disclosed vulnerabilities exist before production release.
- **Approval Gate**: The workflow pauses at the `production` GitHub Environment step. A reviewer must manually approve.
- **Production Retag**: After approval, `az acr import` is used to efficiently retag the `dev-<short-sha>` image in ACR to `vX.Y.Z`.
- **GitOps Commit**: ONLY AFTER successful push, `quickhaul/helm/quickhaul/values-prod.yaml` is updated with `vX.Y.Z` and committed directly to `main` with `[skip ci]`. A Git release tag is also created.
- **Argo CD Prod Deployment**: Argo CD's `quickhaul-prod` Application tracks `targetRevision: main`. It detects the new `vX.Y.Z` tag in `values-prod.yaml` and deploys to the `quickhaul-prod` namespace.

## Manual GitHub Settings & OIDC
To enforce this flow, manual configuration is required in GitHub:
- Main branch protection rules (require PR, require approval).
- A `production` Environment configured with required reviewers.
- Azure OIDC Federated Credentials for `repo:Resolveops-AI/resolveops-application:pull_request`, `repo:Resolveops-AI/resolveops-application:ref:refs/heads/main`, and `repo:Resolveops-AI/resolveops-application:ref:refs/heads/dev`.