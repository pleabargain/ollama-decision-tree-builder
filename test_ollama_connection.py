#!/usr/bin/env python3
"""
Test script to verify Ollama connection and available models
"""
import requests
import json
import sys

def test_ollama_connection():
    """Test connection to Ollama API"""
    print("\n" + "=" * 50)
    print("Ollama Connection Test")
    print("=" * 50)
    
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("\nError: The 'requests' package is required but not installed.")
        print("Install it with: pip install requests")
        return False
    
    # Test connection to Ollama API
    try:
        print("\nTesting connection to Ollama API...")
        response = requests.get("http://localhost:11434/api/version")
        
        if response.status_code == 200:
            version_info = response.json()
            print(f"✓ Connection successful!")
            print(f"✓ Ollama version: {version_info.get('version', 'unknown')}")
        else:
            print(f"✗ Connection failed with status code: {response.status_code}")
            print("  Make sure Ollama is running on http://localhost:11434")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Connection error: Could not connect to Ollama at http://localhost:11434")
        print("  Make sure Ollama is installed and running.")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # List available models
    try:
        print("\nChecking available models...")
        response = requests.get("http://localhost:11434/api/tags")
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            
            if models:
                print(f"✓ Found {len(models)} available models:")
                for model in models:
                    name = model.get('name', 'unknown')
                    size = model.get('size', 0) / (1024 * 1024 * 1024)  # Convert to GB
                    print(f"  - {name} ({size:.2f} GB)")
                
                # Check for recommended models
                recommended_models = ['llama2', 'codellama']
                missing_models = [model for model in recommended_models if not any(m.get('name') == model for m in models)]
                
                if missing_models:
                    print("\nRecommended models not found:")
                    for model in missing_models:
                        print(f"  - {model} (pull with: ollama pull {model})")
            else:
                print("✗ No models found. You need to pull models before using the expert system.")
                print("  Example: ollama pull llama2")
                print("  Example: ollama pull codellama")
        else:
            print(f"✗ Failed to list models with status code: {response.status_code}")
    except Exception as e:
        print(f"✗ Error checking models: {e}")
    
    # Test a simple query
    try:
        print("\nTesting a simple query to Ollama...")
        
        # Use the first available model or default to llama2
        model_to_test = models[0].get('name', 'llama2') if models else 'llama2'
        
        print(f"  Using model: {model_to_test}")
        
        data = {
            "model": model_to_test,
            "prompt": "Say hello in one short sentence.",
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Query successful!")
            print(f"  Response: {result.get('response', 'No response')}")
        else:
            print(f"✗ Query failed with status code: {response.status_code}")
            if model_to_test not in [m.get('name') for m in models]:
                print(f"  Model '{model_to_test}' may not be available. Try pulling it with: ollama pull {model_to_test}")
    except Exception as e:
        print(f"✗ Error testing query: {e}")
    
    print("\nTest completed!")
    return True

if __name__ == "__main__":
    success = test_ollama_connection()
    sys.exit(0 if success else 1)
