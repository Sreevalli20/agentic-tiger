#!/usr/bin/env python3
"""Setup script for GraphProbe AI."""
import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e.stderr}")
        return False


def main():
    """Run setup steps."""
    print("GraphProbe AI Setup")
    print("=" * 50)
    
    # Create necessary directories
    directories = [
        "data/raw",
        "data/processed",
        "data/official_dataset",
        "evaluation/results",
        "evaluation/datasets",
        "evaluation/runners",
        "evaluation/metrics",
        "evaluation/reports",
        "evaluation/schemas",
    ]
    
    print("\nCreating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}")
    
    # Install Python dependencies
    if not run_command(
        "cd backend && python -m pip install -r requirements.txt",
        "Installing Python dependencies"
    ):
        print("\n⚠ Python dependency installation failed. Please install manually.")
        return False
    
    # Install Node dependencies
    if not run_command(
        "cd frontend && npm install",
        "Installing Node dependencies"
    ):
        print("\n⚠ Node dependency installation failed. Please install manually.")
        return False
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("\nCreating .env file from .env.example...")
        import shutil
        shutil.copy(".env.example", ".env")
        print("✓ Created .env file")
        print("⚠ Please update .env with your actual configuration values")
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update .env with your configuration")
    print("2. Set up TigerGraph instance")
    print("3. Place official dataset in data/official_dataset/")
    print("4. Run: python scripts/ingest.py")
    print("5. Run: python backend/app/main.py (backend)")
    print("6. Run: cd frontend && npm run dev (frontend)")


if __name__ == "__main__":
    main()
