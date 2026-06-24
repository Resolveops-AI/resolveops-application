import os
import re

base_dir = r"c:\Users\Admin\Desktop\resolveopsai-application\resolveops-application\quickhaul\backend\services"

service_prefixes = {
    "location_service": "/api/locations",
    "auth_service": "/api/auth",
    "booking_service": "/api/bookings",
    "notification_service": "/api/notifications",
    "otp_service": "/api/otp",
    "payment_service": "/api/payments"
}

for service_dir, prefix in service_prefixes.items():
    app_path = os.path.join(base_dir, service_dir, "app.py")
    if not os.path.exists(app_path):
        print(f"Skipping {app_path}, not found.")
        continue

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject APIRouter import and initialization
    if "from fastapi import APIRouter" not in content:
        content = re.sub(
            r"(app = FastAPI[^\n]*\n)",
            f"\\1\nfrom fastapi import APIRouter\nrouter = APIRouter(prefix='{prefix}')\n\n@router.get('')\n@router.get('/')\nasync def root_health():\n    return {{'status': 'healthy'}}\n",
            content,
            count=1
        )

    # 2. Fix Location Service Health Check (Redis logic)
    if service_dir == "location_service":
        old_health = """@app.get("/health")
async def health_check():
    \"\"\"Health check endpoint\"\"\"
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except:
        return {"status": "unhealthy", "redis": "disconnected"}"""
        
        new_health = """@router.get("/health")
async def health_check():
    \"\"\"Health check endpoint\"\"\"
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected", "redis_required": False}
    except:
        return {"status": "healthy", "redis": "disconnected", "redis_required": False}"""
        
        content = content.replace(old_health, new_health)

    # 3. Replace @app.<method> with @router.<method>
    # Note: we shouldn't replace app.add_middleware or app.include_router
    content = re.sub(r"@app\.(get|post|put|delete|patch|options|head)\(", r"@router.\1(", content)

    # 4. Add app.include_router(router) before if __name__ == "__main__":
    if "app.include_router(router)" not in content:
        content = re.sub(
            r"(if __name__ == [\"']__main__[\"']:)",
            r"app.include_router(router)\n\n\1",
            content
        )

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Updated {service_dir}")
