"""Update .env with correct TigerGraph port."""
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Update with correct port
with open(env_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('TG_PORT='):
        new_lines.append('TG_PORT=443\n')
    else:
        new_lines.append(line)

with open(env_path, 'w') as f:
    f.writelines(new_lines)

print('Updated TG_PORT to 443 in .env')
