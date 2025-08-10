#!/usr/bin/env python3
import ast

try:
    with open('dashboard_endpoints.py', 'r') as f:
        content = f.read()
    
    ast.parse(content)
    print('✅ No syntax errors found')
except SyntaxError as e:
    print(f'❌ Syntax error at line {e.lineno}: {e.text}')
    print(f'Error: {e.msg}')
    
    # Show some context around the error
    lines = content.split('\n')
    start_line = max(0, e.lineno - 5)
    end_line = min(len(lines), e.lineno + 5)
    
    print(f'\nContext around line {e.lineno}:')
    for i in range(start_line, end_line):
        marker = '>>>>' if i == e.lineno - 1 else '    '
        print(f'{marker} {i+1:3d}: {lines[i]}')
