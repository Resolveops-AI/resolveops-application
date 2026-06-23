# Branching and Release Flow

This document details the exact branching flow, PR validation, semantic version calculations, and environmental approval gating for the ResolveOps AI application repository.

## Branching Model

- `dev`: Development integration branch. Direct pushes to this branch run code and Helm validation, and build/push dev images **only for changed services**.
- `main`: Protected production branch. Direct pushes are blocked.

### Development Flow (Push to `dev`)
1. **Trigger**: Code is pushed to `dev`.
2. **Changed Service Detection**: The pipeline identifies which microservices have changed.
3. **Scan**: Runs Sonar and Snyk security scans for changed services.
4. **Validation**: Helm templates are linted and tested for dev/prod.
5. **Build Dev Images**: Builds Docker images tagged as `dev-<short-sha>` **only for changed services**.
6. **Push**: Dev images are pushed to ACR.
7. **GitOps Update**: Updates `values-dev.yaml` with the new dev tag for the changed services and commits back to the `dev` branch using `[skip ci]`.
8. **Deploy**: Argo CD automatically deploys the dev images to the `quickhaul-dev` namespace tracking the `dev` branch.

### Pull Request Flow (PR from `dev` to `main`)
1. **Trigger**: A Pull Request is opened, synchronized, or reopened.
2. **Changed Service Detection**: The pipeline identifies which microservices have changed.
3. **Scan**: Runs Sonar and Snyk security scans for changed services.
4. **Validation**: Helm templates are linted and tested.
5. **Verification Only**: NO images are built, pushed, or deployed. This flow only blocks bad code from merging.

### Production Release Flow (Merge to `main`)
1. **Trigger**: PR is approved and merged into `main`.
2. **Changed Service Detection**: Identifies which microservices have changed.
3. **Scan**: Runs security scans for changed services.
4. **Validation**: Helm templates are tested again.
5. **Semantic Versioning**: Calculates the new semantic version (`vX.Y.Z`) from commit messages using the Conventional Commits specification.
6. **Approval Gate**: Pauses execution and waits for a manual approval on the GitHub `production` Environment.
7. **Release**: Retags the dev candidate images (e.g. `dev-<short-sha>`) as `vX.Y.Z` and pushes the final semantic images to ACR **only for changed services**.
8. **GitOps Update**: Updates `values-prod.yaml` with the semantic version for changed services and commits to `main` using `[skip ci]`.
9. **Git Tag**: Creates a Git tag for `vX.Y.Z`.
10. **Deploy**: Argo CD automatically deploys to the `quickhaul-prod` namespace tracking the `main` branch.

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
- `repo:ResolveOps-AI/resolveops-application:ref:refs/heads/dev`
