# Service CI/CD Mapping

This repository uses a monorepo structure. To optimize the CI/CD pipeline, we employ a dynamic matrix strategy:
**When one service changes, only that specific service's image is built, scanned, pushed, and updated in Helm values.**

## Monorepo Changed-Service Detection Strategy

Instead of building all microservices on every commit, our GitHub Actions workflows (`quickhaul-ci.yml` and `resolveops-ci.yml`) include a `detect-changed-services` job.

1. **Diff Calculation**: The job calculates which files changed based on `git diff`.
2. **Service Mapping Lookup**: It compares the changed paths against `.github/service-map/quickhaul-services.yml` and `.github/service-map/resolveops-services.yml`.
3. **Shared Dependencies**: If changes are detected in shared or common code (e.g., `quickhaul/backend/shared/`), all services that depend on that code are marked for a rebuild.
4. **Dynamic Matrix Generation**: The job outputs a JSON array containing only the services that require updates. Subsequent jobs (`build-scan-push`, `helm-update`) iterate solely over this matrix.
5. **Helm Values Update**: For QuickHaul, the CI pipeline automatically commits updates to only the relevant tag (e.g., `.bookingService.image.tag`) in `values-dev.yaml` (on dev push) or `values-prod.yaml` (on main push).

## QuickHaul Service Mapping Table

Defined in `.github/service-map/quickhaul-services.yml`.

| Service | Source Path | Dockerfile | Image Name | Helm Values Key |
|---------|-------------|------------|------------|-----------------|
| `quickhaul-frontend` | `quickhaul/frontend/**` | `quickhaul/frontend/Dockerfile` | `quickhaul-frontend` | `.frontend.image.tag` |
| `quickhaul-auth` | `quickhaul/backend/services/auth_service/**` | `quickhaul/backend/services/auth_service/Dockerfile` | `quickhaul-auth` | `.authService.image.tag` |
| `quickhaul-booking` | `quickhaul/backend/services/booking_service/**` | `quickhaul/backend/services/booking_service/Dockerfile` | `quickhaul-booking` | `.bookingService.image.tag` |
| `quickhaul-location` | `quickhaul/backend/services/location_service/**` | `quickhaul/backend/services/location_service/Dockerfile` | `quickhaul-location` | `.locationService.image.tag` |
| `quickhaul-notification` | `quickhaul/backend/services/notification_service/**` | `quickhaul/backend/services/notification_service/Dockerfile` | `quickhaul-notification` | `.notificationService.image.tag` |
| `quickhaul-otp` | `quickhaul/backend/services/otp_service/**` | `quickhaul/backend/services/otp_service/Dockerfile` | `quickhaul-otp` | `.otpService.image.tag` |
| `quickhaul-payment` | `quickhaul/backend/services/payment_service/**` | `quickhaul/backend/services/payment_service/Dockerfile` | `quickhaul-payment` | `.paymentService.image.tag` |

## ResolveOps Service Mapping Table

Defined in `.github/service-map/resolveops-services.yml`. Note that ResolveOps does not use automated Helm value updates from the GitHub runner, so Helm keys are not required.

| Service | Source Path | Dockerfile | Image Name |
|---------|-------------|------------|------------|
| `resolveops-frontend` | `frontend/**` | `frontend/Dockerfile` | `frontend` |
| `api-gateway-service` | `services/api-gateway-service/**` | `services/api-gateway-service/Dockerfile` | `api-gateway-service` |
| `auth-service` | `services/auth-service/**` | `services/auth-service/Dockerfile` | `auth-service` |
| `github-intelligence-service` | `services/github-intelligence-service/**` | `services/github-intelligence-service/Dockerfile` | `github-intelligence-service` |
| `azure-intelligence-service` | `services/azure-intelligence-service/**` | `services/azure-intelligence-service/Dockerfile` | `azure-intelligence-service` |
| `aws-intelligence-service` | `services/aws-intelligence-service/**` | `services/aws-intelligence-service/Dockerfile` | `aws-intelligence-service` |
| `ai-rca-service` | `services/ai-rca-service/**` | `services/ai-rca-service/Dockerfile` | `ai-rca-service` |
| `notification-service` | `services/notification-service/**` | `services/notification-service/Dockerfile` | `notification-service` |

## Notifications

Every critical job in our CI pipeline reports failures directly. This provides immediate, job-level feedback for debugging rather than waiting for a single pipeline failure summary.
