with open('dashboard_endpoints.py', 'r') as f:
    lines = f.readlines()

print("Lines around 517:")
for i in range(512, 525):
    if i < len(lines):
        marker = ">>>" if i == 516 else "   "
        print(f"{marker} {i+1:3d}: {lines[i].rstrip()}")
        
print("\nLines around 483:")
for i in range(478, 490):
    if i < len(lines):
        marker = ">>>" if i == 482 else "   "
        print(f"{marker} {i+1:3d}: {lines[i].rstrip()}")
