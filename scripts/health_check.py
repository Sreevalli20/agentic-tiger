#!/usr/bin/env python3
"""Health check script for GraphProbe AI."""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_tigergraph():
    """Check TigerGraph connection."""
    try:
        from pyTigerGraph import TigerGraphConnection
        # Ensure host includes protocol
        host = settings.tg_host
        if not host.startswith(('http://', 'https://')):
            host = f'http://{host}'
        
        conn = TigerGraphConnection(
            host=host,
            restppPort=settings.tg_port,
            gsqlSecret=settings.tg_secret,
            graphname=settings.tg_graphname
        )
        # Test connection
        version = conn.getVersion()
        logger.info(f"✓ TigerGraph connected: {version}")
        return True
    except Exception as e:
        logger.error(f"✗ TigerGraph connection failed: {e}")
        return False


def check_vector_db():
    """Check vector database."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=settings.vector_db_path)
        # Test connection
        collection = client.get_or_create_collection("test")
        logger.info("✓ Vector database accessible")
        return True
    except Exception as e:
        logger.error(f"✗ Vector database check failed: {e}")
        return False


def check_llm():
    """Check LLM configuration."""
    if settings.llm_api_key:
        logger.info("✓ LLM API key configured")
        return True
    else:
        logger.warning("✗ LLM API key not configured")
        return False


def check_dependencies():
    """Check Python dependencies."""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pyTigerGraph",
        "openai",
        "chromadb",
        "pandas",
        "numpy",
    ]
    
    missing = []
    for package in required_packages:
        try:
            # Handle special import names
            if package == "pyTigerGraph":
                __import__("pyTigerGraph")
            else:
                __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.error(f"✗ Missing packages: {', '.join(missing)}")
        return False
    else:
        logger.info("✓ All required packages installed")
        return True


def check_data():
    """Check data directories."""
    data_path = Path(settings.data_path)
    vector_path = Path(settings.vector_db_path)
    
    if not data_path.exists():
        logger.warning(f"✗ Data directory not found: {data_path}")
        return False
    
    logger.info(f"✓ Data directory exists: {data_path}")
    return True


def main():
    """Run all health checks."""
    logger.info("GraphProbe AI Health Check")
    logger.info("=" * 50)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("TigerGraph", check_tigergraph),
        ("Vector Database", check_vector_db),
        ("LLM Configuration", check_llm),
        ("Data Directories", check_data),
    ]
    
    results = {}
    for name, check_func in checks:
        logger.info(f"\nChecking {name}...")
        results[name] = check_func()
    
    logger.info("\n" + "=" * 50)
    logger.info("Health Check Summary:")
    for name, result in results.items():
        status = "✓" if result else "✗"
        logger.info(f"{status} {name}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("\n✓ All checks passed")
        return True
    else:
        logger.warning("\n✗ Some checks failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
