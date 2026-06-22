# Branching and Release Flow

This document details the exact branching flow, PR validation, semantic version calculations, and environmental approval gating for the ResolveOps AI application repository.

## Branching Model

- `dev`: Development integration branch. Direct pushes to this branch only run code and Helm validation. No Docker images are built or pushed to ACR.
- `main`: Protected production branch. Direct pushes are blocked.

### Development Flow (Push to `dev`)
1. **Push to `dev`**: Runs lint testing, SAST, Snyk scan, and Helm validation only.
   - *No image build.*
   - *No ACR push.*
   - *No Helm update.*
   - *No deployment.*

### Pull Request Flow (PR from `dev` to `main`)
This is the dev image creation flow.
1. **Trigger**: A Pull Request is opened, synchronized, or reopened.
2. **Lint Testing**: Runs basic codebase linting and testing.
3. **Security Scan**: Runs SAST and Snyk dependency scanning.
4. **Validation**: Helm templates are linted and tested for dev/prod.
5. **Build Dev Images**: Builds Docker images locally.
6. **Trivy Image Scan**: Scans the locally built images. Fails the workflow if HIGH or CRITICAL vulnerabilities are found.
7. **Push**: Dev images are pushed to ACR (tagged as `dev-pr-<PR_NUMBER>-<short-sha>`) ONLY if Trivy passes.
8. **GitOps Update**: Updates `values-dev.yaml` with the new dev tag ONLY after successful ACR push and commits back to the PR source branch (`dev`) using `[skip ci]`.
9. **Deploy**: Argo CD automatically deploys the dev images to the `quickhaul-dev` namespace tracking the `dev` branch.

### Production Release Flow (Merge to `main`)
This is the production release flow after PR approval and merge.
1. **Trigger**: PR is approved and merged into `main`.
2. **Lint Testing**: Runs basic codebase linting and testing again.
3. **Security Scan**: Runs SAST and Snyk scanning again.
4. **Validation**: Helm templates are tested again.
5. **Semantic Versioning**: Calculates the new semantic version (`vX.Y.Z`) from commit messages.
6. **Build Prod Candidates**: Builds production candidate images locally as `main-<short-sha>`.
7. **Trivy Image Scan**: Scans the production candidate images.
8. **Tag Verification**: Checks ACR to ensure `vX.Y.Z` does not already exist. Fails the workflow if it does.
9. **Approval Gate**: Pauses execution and waits for a manual approval on the GitHub `production` Environment.
10. **Release**: After approval, retags `main-<short-sha>` as `vX.Y.Z` and pushes the final semantic images to ACR.
11. **GitOps Update**: Updates `values-prod.yaml` with the semantic version ONLY after successful semantic image push and commits to `main` using `[skip ci]`.
12. **Git Tag**: Creates a Git tag for `vX.Y.Z`.
13. **Deploy**: Argo CD automatically deploys to the `quickhaul-prod` namespace tracking the `main` branch.

## Manual GitHub Settings Required

To enforce this flow, the following GitHub Repository settings must be manually configured:

1. **Branch Protection (`main`)**:
   - Require a pull request before merging.
   - Require at least 1 approval.
   - Require status checks to pass before merging.
   - Do not allow bypassing the above settings.
   - Restrict who can push to matching branches (block direct push).
2. **Environments**:
   - Create an environment named `production`.
   - Add required reviewers to the `production` environment to enforce the manual release gate.
3. **Azure OIDC Federated Credentials**:
   - `repo:Resolveops-AI/resolveops-application:pull_request`
   - `repo:Resolveops-AI/resolveops-application:ref:refs/heads/main`
