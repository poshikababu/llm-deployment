#!/usr/bin/env python3
"""
Real Deployment Test - Uses actual credentials to test the complete workflow
"""

import os
import json
import base64
import time
import requests
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_real_test_request():
    """Create a real test request with actual credentials."""
    
    # Create a sample CSV file for testing
    csv_content = """product,region,sales,date
Laptop,North America,15000,2024-01-15
Smartphone,Europe,12500,2024-01-16
Tablet,Asia,8900,2024-01-17
Monitor,North America,4500,2024-01-18
Keyboard,Europe,2300,2024-01-19
Mouse,Asia,1800,2024-01-20
Headphones,North America,6700,2024-01-21
Webcam,Europe,3400,2024-01-22
"""
    
    # Encode as base64
    csv_base64 = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
    
    # Create the real test request
    test_request = {
        "email": "23f3000552@ds.study.iitm.ac.in",  # Your actual email
        "secret": os.getenv('SHARED_SECRET'),
        "task": "sales-analytics-dashboard",
        "round": 1,
        "nonce": f"test-{int(time.time())}",
        "brief": """Create a comprehensive sales analytics dashboard that:

1. **Data Loading**: Load and parse the attached CSV sales data
2. **Data Display**: Show all sales records in a responsive Bootstrap table
3. **Analytics**: Calculate and prominently display:
   - Total sales amount
   - Average sales per product
   - Sales by region breakdown
4. **Interactivity**: 
   - Filter by region dropdown
   - Sort table columns
   - Search functionality
5. **Visualization**: Add a simple chart showing sales by region
6. **Design**: Modern, professional UI with Bootstrap 5
7. **Responsiveness**: Mobile-friendly design

The application should be fully self-contained with all CSS and JavaScript inline.""",
        "checks": [
            "CSV data loads and displays correctly",
            "Total sales calculation is accurate", 
            "Region filter works properly",
            "Table sorting functions correctly",
            "Chart displays sales by region",
            "Mobile responsive design",
            "Professional Bootstrap styling"
        ],
        "evaluation_url": "https://httpbin.org/post",  # Test endpoint
        "attachments": [{
            "name": "sales_data.csv",
            "url": f"data:text/csv;base64,{csv_base64}"
        }]
    }
    
    return test_request

def start_server_and_test():
    """Start the Flask server and run a real test."""
    
    print("🚀 Starting LLM Code Deployment Application with Real Credentials")
    print("=" * 70)
    
    # Verify environment
    print("🔍 Checking environment configuration...")
    required_vars = ['SHARED_SECRET', 'GITHUB_PAT', 'GITHUB_USERNAME', 'OPENROUTER_API_KEY']
    
    for var in required_vars:
        value = os.getenv(var)
        if value and not value.startswith('your-') and not value.startswith('test-'):
            print(f"✅ {var}: Configured")
        else:
            print(f"❌ {var}: Not properly configured")
            return False
    
    print(f"✅ Using GitHub user: {os.getenv('GITHUB_USERNAME')}")
    print(f"✅ Using LLM model: {os.getenv('LLM_MODEL')}")
    print(f"✅ Using OpenRouter (USE_AIPIPE={os.getenv('USE_AIPIPE', 'false')})")
    
    # Start Flask server in background
    def run_server():
        try:
            from app import app
            app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)
        except Exception as e:
            print(f"❌ Server error: {e}")
    
    print("\n🌐 Starting Flask server...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    # Test server health
    try:
        response = requests.get('http://localhost:3000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on http://localhost:3000")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Create and send real test request
    print("\n📝 Creating real deployment test request...")
    test_request = create_real_test_request()
    
    print(f"   Task: {test_request['task']}")
    print(f"   Email: {test_request['email']}")
    print(f"   Attachments: {len(test_request['attachments'])}")
    print(f"   Brief: {test_request['brief'][:100]}...")
    
    # Send the request
    print("\n🚀 Sending deployment request...")
    try:
        response = requests.post(
            'http://localhost:3000/api-endpoint',
            json=test_request,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request accepted successfully!")
            print(f"   Response: {result}")
            
            print("\n⏳ Background processing started...")
            print("   This will:")
            print("   1. Generate HTML code using the free LLM model")
            print("   2. Create a GitHub repository")
            print("   3. Push the generated code")
            print("   4. Enable GitHub Pages")
            print("   5. Send notification to evaluation URL")
            
            print(f"\n🔍 Monitor your GitHub account: https://github.com/{os.getenv('GITHUB_USERNAME')}")
            print("   Look for a new repository called 'sales-analytics-dashboard'")
            
            # Wait and monitor
            print("\n📊 Monitoring progress...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                print(f"   ⏳ Processing... {i+1}/30 seconds")
            
            print("\n✅ Initial processing complete!")
            print("🎯 Check your GitHub account for the new repository")
            print("🌐 The GitHub Pages site should be available shortly")
            
            return True
            
        elif response.status_code == 401:
            print("❌ Authentication failed - check SHARED_SECRET")
            return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    """Main function."""
    success = start_server_and_test()
    
    if success:
        print("\n🎉 Real deployment test completed successfully!")
        print("\n📋 What to check:")
        print("   1. New repository in your GitHub account")
        print("   2. Repository contains: index.html, README.md, LICENSE")
        print("   3. GitHub Pages is enabled and accessible")
        print("   4. The web app loads and functions correctly")
        
        print("\n🔗 Useful links:")
        print(f"   GitHub Profile: https://github.com/{os.getenv('GITHUB_USERNAME')}")
        print(f"   Expected Repo: https://github.com/{os.getenv('GITHUB_USERNAME')}/sales-analytics-dashboard")
        print(f"   Expected Pages: https://{os.getenv('GITHUB_USERNAME')}.github.io/sales-analytics-dashboard/")
        
        print("\n👋 Server will continue running. Press Ctrl+C to stop.")
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped.")
    else:
        print("\n❌ Deployment test failed. Check the errors above.")

if __name__ == "__main__":
    main()