"""Test TigerGraph authentication directly."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

print(f'Env path: {env_path}')
print(f'Env exists: {env_path.exists()}')
print(f'TG_HOST: {os.environ.get("TG_HOST")}')
print(f'TG_PORT: {os.environ.get("TG_PORT")}')
print(f'TG_GRAPHNAME: {os.environ.get("TG_GRAPHNAME")}')
print(f'TG_SECRET: {os.environ.get("TG_SECRET")}')
print(f'TG_SECRET length: {len(os.environ.get("TG_SECRET", ""))}')

# Now test connection
from pyTigerGraph import TigerGraphConnection

host = os.environ.get('TG_HOST')
port = int(os.environ.get('TG_PORT', 443))
secret = os.environ.get('TG_SECRET')
graphname = os.environ.get('TG_GRAPHNAME', 'Transaction_Fraud')

print(f'\nTesting connection to {host}:{port}')

try:
    # Try without secret first
    print('Trying connection without secret...')
    conn1 = TigerGraphConnection(
        host=host,
        restppPort=port,
        graphname=""
    )
    
    version1 = conn1.getVersion()
    print(f'Version without secret: {version1}')
    
except Exception as e:
    print(f'Error without secret: {e}')

try:
    # Try with secret
    print('\nTrying connection with secret...')
    conn2 = TigerGraphConnection(
        host=host,
        restppPort=port,
        gsqlSecret=secret,
        graphname=""
    )
    
    # Try getToken
    print('Trying getToken...')
    token = conn2.getToken(secret)
    print(f'Token: {token}')
    
    # Try version with token
    version2 = conn2.getVersion()
    print(f'Version with secret: {version2}')
    
    # Set graph name
    conn2.graphname = graphname
    print(f'Graph set to: {graphname}')
    
    # Try to get schema
    schema = conn2.getSchema()
    print(f'Schema vertex types: {[vt["Name"] for vt in schema.get("VertexTypes", [])]}')
    
except Exception as e:
    print(f'Error with secret: {e}')
    import traceback
    traceback.print_exc()
