#!/usr/bin/env python3
"""
Quick start script for NYC Live Aircraft Tracker.
Checks setup and provides guidance for first-time users.
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    required = ['requests', 'dotenv', 'rich', 'geopy']
    
    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
        except ImportError:
            missing.append(package if package != 'dotenv' else 'python-dotenv')
    
    return missing


def check_config():
    """Check if configuration is set up."""
    env_exists = Path('.env').exists()
    config_exists = Path('config.json').exists()
    
    return env_exists, config_exists


def main():
    """Main setup check and guide."""
    print("\n" + "="*70)
    print("NYC LIVE AIRCRAFT TRACKER - SETUP CHECK")
    print("="*70 + "\n")
    
    # Check dependencies
    print("📦 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"   ❌ Missing packages: {', '.join(missing)}")
        print(f"\n   To install, run:")
        print(f"   pip install -r requirements.txt\n")
        sys.exit(1)
    else:
        print("   ✅ All dependencies installed\n")
    
    # Check configuration
    print("⚙️  Checking configuration...")
    env_exists, config_exists = check_config()
    
    if not config_exists:
        print("   ❌ config.json not found")
        sys.exit(1)
    else:
        print("   ✅ config.json found")
    
    if not env_exists:
        print("   ⚠️  .env file not found")
        print("\n   For best experience with real data:")
        print("   1. Copy .env.example to .env:")
        print("      cp .env.example .env")
        print("   2. Edit .env and add your OpenSky credentials")
        print("   3. Or run without credentials (limited rate limits)")
        print("\n   To test without API credentials, run: python demo.py\n")
    else:
        print("   ✅ .env file found")
        
        # Check if credentials are set
        from dotenv import load_dotenv
        load_dotenv()
        
        username = os.getenv('OPENSKY_USERNAME')
        password = os.getenv('OPENSKY_PASSWORD')
        
        if not username or not password or 'your_' in username.lower():
            print("   ⚠️  OpenSky credentials not configured in .env")
            print("      You can still use the API but with limited rate limits")
        else:
            print("   ✅ OpenSky credentials configured")
    
    print("\n" + "="*70)
    print("READY TO START!")
    print("="*70)
    print("\nAvailable commands:")
    print("  python demo.py    - Run demo with simulated data (no API needed)")
    print("  python main.py    - Run live tracker with real OpenSky data")
    print("\nPress Ctrl+C to stop the tracker at any time.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
