#!/usr/bin/env python3
"""
Simple runner script for the LLM Code Deployment Application
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set."""
    required_vars = {
        'SHARED_SECRET': 'Shared secret for request authentication',
        'GITHUB_PAT': 'GitHub Personal Access Token',
        'GITHUB_USERNAME': 'GitHub username',
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  {var}: {description}")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        print("\n".join(missing_vars))
        print("\nPlease configure your .env file with the required values.")
        return False
    
    # Check LLM configuration
    use_aipipe = os.getenv('USE_AIPIPE', 'false').lower() == 'true'
    if use_aipipe:
        if not os.getenv('AIPIPE_TOKEN'):
            print("❌ AIPIPE_TOKEN is required when USE_AIPIPE=true")
            return False
        print("✅ Using AI Pipe for LLM generation")
    else:
        if not os.getenv('OPENROUTER_API_KEY'):
            print("❌ OPENROUTER_API_KEY is required when USE_AIPIPE=false")
            return False
        print("✅ Using OpenRouter for LLM generation")
    
    print("✅ Environment configuration looks good")
    return True

def main():
    """Main entry point."""
    print("🚀 LLM Code Deployment Application")
    print("=" * 40)
    
    if not check_environment():
        sys.exit(1)
    
    print("\n📝 Configuration Summary:")
    print(f"   GitHub User: {os.getenv('GITHUB_USERNAME')}")
    print(f"   LLM Provider: {'AI Pipe' if os.getenv('USE_AIPIPE', 'false').lower() == 'true' else 'OpenRouter'}")
    print(f"   Model: {os.getenv('LLM_MODEL', 'meta-llama/llama-3.1-8b-instruct:free')}")
    
    print("\n🌐 Starting Flask server...")
    
    try:
        from app import app
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 3000)),
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()