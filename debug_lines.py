import sys

try:
    with open('dashboard_endpoints.py', 'r') as f:
        lines = f.readlines()
    
    print("Lines around the error:")
    for i in range(510, 525):
        if i < len(lines):
            marker = ">>>" if i == 516 else "   "
            print(f"{marker} {i+1:3d}: {lines[i].rstrip()}")
except Exception as e:
    print(f"Error: {e}")
