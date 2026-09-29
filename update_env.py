"""Update .env with production TigerGraph host."""
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Update with production values
with open(env_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('TG_HOST='):
        new_lines.append('TG_HOST=https://tg-b9e4f040-4261-4150-8392-8fad5e33df28.tg-2635877100.i.tgcloud.io\n')
    else:
        new_lines.append(line)

with open(env_path, 'w') as f:
    f.writelines(new_lines)

print('Updated TG_HOST in .env')
