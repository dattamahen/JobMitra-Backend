"""
Diagnostic script for JobMitra Backend
"""

print("🔍 JobMitra Backend Diagnostic")
print("=" * 40)

# Test Python basics
try:
    import sys
    print(f"✅ Python version: {sys.version}")
except Exception as e:
    print(f"❌ Python issue: {e}")

# Test required packages
packages = [
    ("fastapi", "FastAPI framework"),
    ("uvicorn", "ASGI server"),
    ("motor", "Async MongoDB driver"),
    ("pymongo", "MongoDB driver"),
    ("pydantic", "Data validation"),
    ("python-dotenv", "Environment variables")
]

missing_packages = []

for package, description in packages:
    try:
        __import__(package)
        print(f"✅ {package} - {description}")
    except ImportError:
        print(f"❌ {package} - {description} (MISSING)")
        missing_packages.append(package)

if missing_packages:
    print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
    print("Run: pip install " + " ".join(missing_packages))
else:
    print("\n🎉 All required packages are installed!")

# Test file imports
print("\n🔍 Testing file imports...")
try:
    from crew_agent_simple import run_crew_ai
    print("✅ crew_agent_simple imports")
except Exception as e:
    print(f"❌ crew_agent_simple: {e}")

try:
    from db_simple import db
    print("✅ db_simple imports")
except Exception as e:
    print(f"❌ db_simple: {e}")

try:
    from api_routes import router
    print("✅ api_routes imports")
except Exception as e:
    print(f"❌ api_routes: {e}")

try:
    import main
    print("✅ main.py imports")
except Exception as e:
    print(f"❌ main.py: {e}")

print("\n" + "=" * 40)
print("Diagnostic complete!")
