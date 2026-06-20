import subprocess
import sys
import time
import signal
from pathlib import Path

services = [
    ("Location Service", "services.location_service.app:app", 8001),
    ("Auth Service", "services.auth_service.main:app", 8002),
    ("Booking Service", "services.booking_service.app:app", 8003),
    ("Notification Service", "services.notification_service.app:app", 8004),
    ("OTP Service", "services.otp_service.app:app", 8005),
]

processes = []


def start_service(name, module, port):
    cmd = [sys.executable, "-m", "uvicorn", module, "--host", "127.0.0.1", "--port", str(port), "--reload"]
    print(f"Starting {name} on port {port}...")
    return subprocess.Popen(cmd, cwd=Path(__file__).parent)


def shutdown(signum, frame):
    try:
        print("\nShutting down all services...")
    except RuntimeError:
        pass  # Ignore reentrant print error
    for p in processes:
        p.terminate()
    time.sleep(2)
    for p in processes:
        if p.poll() is None:
            p.kill()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("=" * 60)
    print("QuickHaul Microservices Launcher")
    print("=" * 60)
    print()

    for name, module, port in services:
        p = start_service(name, module, port)
        processes.append(p)
        time.sleep(2)  # Stagger startup to avoid conflicts

    print()
    print("All services started:")
    print("  Location Service:   http://127.0.0.1:8001")
    print("  Auth Service:       http://127.0.0.1:8002")
    print("  Booking Service:    http://127.0.0.1:8003")
    print("  Notification Service: http://127.0.0.1:8004")
    print("  OTP Service:        http://127.0.0.1:8005")
    print()
    print("Press Ctrl+C to stop all services")
    print()

    # Monitor processes
    while True:
        for i, (name, _, _) in enumerate(services):
            if processes[i].poll() is not None:
                print(f"WARNING: {name} exited with code {processes[i].returncode}")
        time.sleep(1)
