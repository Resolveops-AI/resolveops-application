# Branching and Release Flow

This document details the exact branching flow, PR validation, semantic version calculations, and environmental approval gating for the ResolveOps AI application repository.

## Branching Model

- `dev`: Development integration branch. Direct pushes to this branch only run code and Helm validation. No Docker images are built or pushed to ACR.
- `main`: Protected production branch. Direct pushes are blocked.

### Development Flow (Push to `dev`)
1. **Push to `dev`**: Runs security scan and Helm validation only.
   - *No image build.*
   - *No ACR push.*
   - *No deployment.*

### Pull Request Flow (PR from `dev` to `main`)
1. **Trigger**: A Pull Request is opened, synchronized, or reopened.
2. **Scan**: Runs Trivy security scan.
3. **Validation**: Helm templates are linted and tested for dev/prod.
4. **Build Dev Images**: Builds Docker images tagged as `dev-pr-<PR_NUMBER>-<short-sha>`.
5. **Push**: Dev images are pushed to ACR.
6. **GitOps Update**: Updates `values-dev.yaml` with the new dev tag and commits back to the PR source branch (`dev`) using `[skip ci]`.
7. **Deploy**: Argo CD automatically deploys the dev images to the `quickhaul-dev` namespace tracking the `dev` branch.

### Production Release Flow (Merge to `main`)
1. **Trigger**: PR is approved and merged into `main`.
2. **Scan**: Runs Trivy security scan again.
3. **Validation**: Helm templates are tested again.
4. **Build Prod Candidates**: Builds production candidate images tagged as `main-<short-sha>`.
5. **Semantic Versioning**: Calculates the new semantic version (`vX.Y.Z`) from commit messages using the Conventional Commits specification.
6. **Tag Verification**: Checks ACR to ensure `vX.Y.Z` does not already exist. Fails the workflow if it does.
7. **Approval Gate**: Pauses execution and waits for a manual approval on the GitHub `production` Environment.
8. **Release**: Retags `main-<short-sha>` as `vX.Y.Z` and pushes the final semantic images to ACR.
9. **GitOps Update**: Updates `values-prod.yaml` with the semantic version and commits to `main` using `[skip ci]`.
10. **Git Tag**: Creates a Git tag for `vX.Y.Z`.
11. **Deploy**: Argo CD automatically deploys to the `quickhaul-prod` namespace tracking the `main` branch.

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

## Azure OIDC Federated Credentials

Since the CI/CD pipeline pushes to ACR on both `pull_request` and `push` to `main`, the Azure AD Application (Service Principal) used for OIDC authentication requires the following federated credentials:
- `repo:ResolveOps-AI/resolveops-application:pull_request`
- `repo:ResolveOps-AI/resolveops-application:ref:refs/heads/main`
