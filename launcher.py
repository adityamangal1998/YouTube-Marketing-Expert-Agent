#!/usr/bin/env python3
"""
YouTube Marketing Expert Agent Launcher
Cross-platform launcher script
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_virtual_environment():
    """Check if we're in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def check_env_file():
    """Check if .env file exists and is configured"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Please run the configuration setup:")
        print("python configure.py")
        return False
    
    # Check if .env has been configured
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_youtube_api_key_here' in content or 'your_aws_access_key_here' in content:
            print("⚠️  .env file found but not configured")
            print("Please run the configuration setup:")
            print("python configure.py")
            return False
    
    return True

def run_streamlit():
    """Run the Streamlit application"""
    print("🚀 Starting YouTube Marketing Expert Agent...")
    print("The application will open in your default web browser")
    print("Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'main.py'])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    """Main launcher function"""
    print("🎬 YouTube Marketing Expert Agent Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check if in virtual environment
    if check_virtual_environment():
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in a virtual environment (recommended but not required)")
    
    # Check if Streamlit is installed
    if not check_streamlit():
        print("📦 Streamlit not found, installing requirements...")
        if not install_requirements():
            print("❌ Failed to install requirements. Please run manually:")
            print("pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✅ Streamlit is installed")
    
    # Check environment configuration
    if not check_env_file():
        response = input("\nWould you like to run the configuration setup now? (y/N): ")
        if response.lower() in ['y', 'yes']:
            try:
                subprocess.run([sys.executable, 'configure.py'])
                if not check_env_file():
                    print("Configuration incomplete. Exiting.")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Error running configuration: {e}")
                sys.exit(1)
        else:
            print("Configuration required. Exiting.")
            sys.exit(1)
    else:
        print("✅ Configuration file found and configured")
    
    # Run application
    print("\n" + "=" * 50)
    run_streamlit()

if __name__ == "__main__":
    main()
