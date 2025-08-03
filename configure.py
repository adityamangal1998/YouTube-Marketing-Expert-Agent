"""
Configuration helper for YouTube Marketing Expert Agent
Run this script to help set up your environment variables
"""

import os
from dotenv import load_dotenv, set_key

def setup_configuration():
    """Interactive setup for environment variables"""
    print("🛠️  YouTube Marketing Expert Agent - Configuration Setup")
    print("=" * 60)
    print("This script will help you configure your API credentials.")
    print("You can skip any step by pressing Enter (will use existing value).\n")
    
    env_file = ".env"
    load_dotenv(env_file)
    
    # YouTube API Key
    print("1️⃣  YouTube Data API v3 Configuration")
    print("   Get your API key from: https://console.cloud.google.com/")
    print("   Enable YouTube Data API v3 for your project")
    
    current_youtube_key = os.getenv('YOUTUBE_API_KEY', '')
    if current_youtube_key and current_youtube_key != 'your_youtube_api_key_here':
        print(f"   Current: {current_youtube_key[:10]}..." + "*" * 20)
    
    youtube_key = input("   Enter YouTube API Key (or press Enter to keep current): ").strip()
    if youtube_key:
        set_key(env_file, 'YOUTUBE_API_KEY', youtube_key)
        print("   ✅ YouTube API key saved")
    
    # AWS Configuration
    print("\n2️⃣  AWS Bedrock Configuration")
    print("   Get your credentials from: https://console.aws.amazon.com/")
    print("   Ensure you have access to Claude Sonnet 3.5 model")
    
    current_aws_key = os.getenv('AWS_ACCESS_KEY_ID', '')
    if current_aws_key and current_aws_key != 'your_aws_access_key_here':
        print(f"   Current Access Key: {current_aws_key[:10]}..." + "*" * 10)
    
    aws_access_key = input("   Enter AWS Access Key ID (or press Enter to keep current): ").strip()
    if aws_access_key:
        set_key(env_file, 'AWS_ACCESS_KEY_ID', aws_access_key)
        print("   ✅ AWS Access Key saved")
    
    current_aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    if current_aws_secret and current_aws_secret != 'your_aws_secret_key_here':
        print(f"   Current Secret Key: " + "*" * 20)
    
    aws_secret_key = input("   Enter AWS Secret Access Key (or press Enter to keep current): ").strip()
    if aws_secret_key:
        set_key(env_file, 'AWS_SECRET_ACCESS_KEY', aws_secret_key)
        print("   ✅ AWS Secret Key saved")
    
    current_region = os.getenv('AWS_REGION', 'us-east-1')
    print(f"   Current Region: {current_region}")
    
    aws_region = input("   Enter AWS Region [us-east-1] (or press Enter to keep current): ").strip()
    if aws_region:
        set_key(env_file, 'AWS_REGION', aws_region)
        print("   ✅ AWS Region saved")
    elif not current_region:
        set_key(env_file, 'AWS_REGION', 'us-east-1')
        print("   ✅ AWS Region set to default (us-east-1)")
    
    print("\n🎉 Configuration complete!")
    print("\nNext steps:")
    print("1. Run the test script: python test_setup.py")
    print("2. If tests pass, run the app: streamlit run main.py")
    
    # Test configuration
    test_now = input("\nWould you like to test the configuration now? (y/N): ").strip().lower()
    if test_now in ['y', 'yes']:
        print("\n" + "="*50)
        try:
            from test_setup import main as test_main
            test_main()
        except ImportError:
            print("❌ Could not import test script. Please run 'python test_setup.py' manually.")

def show_current_config():
    """Show current configuration"""
    print("📋 Current Configuration")
    print("=" * 30)
    
    load_dotenv()
    
    configs = [
        ("YouTube API Key", "YOUTUBE_API_KEY"),
        ("AWS Access Key ID", "AWS_ACCESS_KEY_ID"),
        ("AWS Secret Access Key", "AWS_SECRET_ACCESS_KEY"),
        ("AWS Region", "AWS_REGION")
    ]
    
    for name, env_var in configs:
        value = os.getenv(env_var, 'Not set')
        if env_var == "AWS_SECRET_ACCESS_KEY" and value != 'Not set':
            display_value = "*" * 20  # Hide secret key
        elif value != 'Not set' and 'your_' not in value.lower():
            display_value = value[:15] + "..." if len(value) > 15 else value
        else:
            display_value = value
        
        print(f"{name}: {display_value}")

def main():
    """Main configuration interface"""
    while True:
        print("\n🛠️  Configuration Menu")
        print("1. Setup/Update Configuration")
        print("2. Show Current Configuration")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == '1':
            setup_configuration()
        elif choice == '2':
            show_current_config()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
