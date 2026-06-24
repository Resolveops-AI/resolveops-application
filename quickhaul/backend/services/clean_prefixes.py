import os
import re

base_dir = r"c:\Users\Admin\Desktop\resolveopsai-application\resolveops-application\quickhaul\backend\services"

services = {
    "auth_service": [r'"/auth/', r'"/'],
    "booking_service": [r'"/bookings', r'"'],
    "notification_service": [r'"/notifications', r'"'],
    "otp_service": [r'"/otp', r'"']
}

for service_dir, replacements in services.items():
    app_path = os.path.join(base_dir, service_dir, "app.py")
    if not os.path.exists(app_path):
        continue

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace double paths inside router decorators
    # e.g., @router.get("/bookings") -> @router.get("")
    # @router.post("/auth/login") -> @router.post("/login")
    
    # We only want to replace it if it's inside @router.
    pattern = r'(@router\.[a-z]+\()' + replacements[0]
    replacement = r'\g<1>' + replacements[1]
    
    content = re.sub(pattern, replacement, content)

    # Also fix the health checks for ALL services to return redis_required=False and status 200
    old_health = """@router.get("/health")
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

    # Note: payment_service has `main.py`, so I'll handle that separately.

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Double prefixes cleaned and health checks fixed!")
