with open('dashboard_endpoints.py', 'r') as f:
    lines = f.readlines()

for i in range(515, 525):
    if i < len(lines):
        print(f"{i+1}: {lines[i].rstrip()}")
