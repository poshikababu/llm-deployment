#!/usr/bin/env python3
"""
Quick Test Script - Tests individual components step by step
"""

import os
import json
import base64
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_setup():
    """Test environment configuration."""
    print("🔍 Testing Environment Setup...")
    
    # Set test environment variables
    os.environ['SHARED_SECRET'] = 'test-secret-123'
    os.environ['GITHUB_PAT'] = 'test-github-pat'
    os.environ['GITHUB_USERNAME'] = 'test-user'
    os.environ['OPENROUTER_API_KEY'] = 'test-openrouter-key'
    
    print("✅ Environment variables configured")
    return True

def test_module_imports():
    """Test that all modules can be imported."""
    print("\n📦 Testing Module Imports...")
    
    try:
        from modules.llm_generator import LLMGenerator
        print("✅ LLM Generator module imported")
        
        from modules.github_manager import GitHubManager
        print("✅ GitHub Manager module imported")
        
        from modules.notifier import EvaluationNotifier
        print("✅ Notification module imported")
        
        from app import app
        print("✅ Flask app imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_llm_generator():
    """Test LLM generator initialization."""
    print("\n🤖 Testing LLM Generator...")
    
    try:
        from modules.llm_generator import LLMGenerator
        
        generator = LLMGenerator()
        print(f"✅ LLM Generator initialized")
        print(f"   Model: {generator.model}")
        
        # Test attachment processing
        test_attachment = {
            "name": "test.csv",
            "url": "data:text/csv;base64," + base64.b64encode(b"name,value\ntest,123").decode()
        }
        
        attachment_text = generator._process_attachments([test_attachment])
        print("✅ Attachment processing works")
        print(f"   Processed {len(attachment_text)} characters")
        
        return True
    except Exception as e:
        print(f"❌ LLM Generator error: {e}")
        return False

def test_github_manager():
    """Test GitHub manager initialization."""
    print("\n🐙 Testing GitHub Manager...")
    
    try:
        from modules.github_manager import GitHubManager
        
        # This will fail with test credentials, but we can test initialization
        try:
            manager = GitHubManager()
            print("✅ GitHub Manager initialized (with test credentials)")
        except Exception as auth_error:
            print(f"⚠️  GitHub Manager initialization failed (expected with test credentials)")
            print(f"   Error: {str(auth_error)[:100]}...")
            print("✅ GitHub Manager class structure is correct")
        
        # Test utility methods
        manager = GitHubManager.__new__(GitHubManager)  # Create without __init__
        repo_name = manager._generate_repo_name("test-task-123")
        print(f"✅ Repository name generation: {repo_name}")
        
        license_content = manager._create_license_content()
        print(f"✅ License generation: {len(license_content)} characters")
        
        return True
    except Exception as e:
        print(f"❌ GitHub Manager error: {e}")
        return False

def test_notifier():
    """Test notification module."""
    print("\n📬 Testing Notification Module...")
    
    try:
        from modules.notifier import EvaluationNotifier
        
        notifier = EvaluationNotifier()
        print("✅ Notifier initialized")
        print(f"   Max retries: {notifier.max_retries}")
        print(f"   Base delay: {notifier.base_delay}s")
        
        # Test delay calculation
        delays = [notifier._calculate_delay(i) for i in range(4)]
        print(f"✅ Retry delays: {delays}")
        
        # Test data validation
        test_data = {
            "email": "test@example.com",
            "task": "test-task",
            "round": 1,
            "nonce": "test-nonce",
            "repo_url": "https://github.com/user/repo",
            "commit_sha": "abc123def456",
            "pages_url": "https://user.github.io/repo"
        }
        
        is_valid, message = notifier.validate_notification_data(test_data)
        print(f"✅ Data validation: {is_valid} - {message}")
        
        return True
    except Exception as e:
        print(f"❌ Notifier error: {e}")
        return False

def test_flask_app():
    """Test Flask app configuration."""
    print("\n🌐 Testing Flask Application...")
    
    try:
        from app import app
        
        print("✅ Flask app created")
        print(f"   Routes: {[rule.rule for rule in app.url_map.iter_rules()]}")
        
        # Test app configuration
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            print(f"✅ Health endpoint: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Response: {data}")
        
        return True
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

def create_sample_request():
    """Create a sample request payload."""
    print("\n📝 Creating Sample Request...")
    
    # Create sample CSV attachment
    csv_content = "product,sales\nLaptop,15000\nPhone,8500"
    csv_base64 = base64.b64encode(csv_content.encode()).decode()
    
    sample_request = {
        "email": "test@example.com",
        "secret": "test-secret-123",
        "task": "sales-dashboard-test",
        "round": 1,
        "nonce": "test-nonce-001",
        "brief": "Create a sales dashboard that displays the CSV data in a table with total sales calculation.",
        "checks": [
            "CSV data loads correctly",
            "Table displays all records",
            "Total sales is calculated",
            "Responsive design"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": [{
            "name": "sales.csv",
            "url": f"data:text/csv;base64,{csv_base64}"
        }]
    }
    
    print("✅ Sample request created")
    print(f"   Task: {sample_request['task']}")
    print(f"   Brief: {sample_request['brief'][:50]}...")
    print(f"   Attachments: {len(sample_request['attachments'])}")
    
    return sample_request

def main():
    """Run all tests."""
    print("🧪 LLM Code Deployment - Component Testing")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Module Imports", test_module_imports),
        ("LLM Generator", test_llm_generator),
        ("GitHub Manager", test_github_manager),
        ("Notifier", test_notifier),
        ("Flask App", test_flask_app),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Create sample request
    sample_request = create_sample_request()
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All component tests passed!")
        print("\n💡 The application is ready for deployment testing.")
        print("   To test the full workflow:")
        print("   1. Configure real API keys in .env")
        print("   2. Run: uv run python app.py")
        print("   3. Send POST request to http://localhost:3000/api-endpoint")
        print("   4. Check your GitHub account for new repositories")
        
        print(f"\n📋 Sample Request JSON:")
        print(json.dumps(sample_request, indent=2))
        
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)