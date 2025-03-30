#!/usr/bin/env python3
"""
Utility functions for working with Ollama
"""
import requests
import sys

def check_ollama_running():
    """
    Check if Ollama is running and accessible
    Returns True if running, False otherwise
    """
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✓ Ollama is running (version: {version_info.get('version', 'unknown')})")
            return True
        else:
            print(f"✗ Ollama API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to Ollama at http://localhost:11434")
        print("  Make sure Ollama is installed and running.")
        return False
    except Exception as e:
        print(f"✗ Unexpected error checking Ollama: {e}")
        return False

def get_available_models():
    """
    Get a list of available Ollama models
    Returns a list of model names, or an empty list if none are found
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model.get('name', 'unknown') for model in models]
        else:
            print(f"✗ Failed to list models with status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Error checking models: {e}")
        return []

def select_model(default_model="gemma3"):
    """
    Prompt the user to select an Ollama model
    Returns the selected model name or the default if none is selected
    """
    # First check if Ollama is running
    if not check_ollama_running():
        print("\nOllama must be running to use this application.")
        print("Please start Ollama and try again.")
        print("If Ollama is not installed, visit https://ollama.ai/ for installation instructions.")
        sys.exit(1)
    
    # Get available models
    available_models = get_available_models()
    
    if not available_models:
        print("\nNo models found. You need to pull models before using the expert system.")
        print("Example: ollama pull gemma3")
        print("Example: ollama pull llama2")
        sys.exit(1)
    
    # Check if default model is available, if not use the first available model
    if default_model not in available_models:
        default_model = available_models[0]
    
    # Display available models
    print("\nAvailable models:")
    for i, model in enumerate(available_models, 1):
        if model == default_model:
            print(f"{i}. {model} (default)")
        else:
            print(f"{i}. {model}")
    
    # Prompt user to select a model
    while True:
        choice = input(f"\nSelect a model (1-{len(available_models)}, or press Enter for default): ")
        
        if choice == "":
            print(f"Using default model: {default_model}")
            return default_model
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_models):
                selected_model = available_models[choice_idx]
                print(f"Selected model: {selected_model}")
                return selected_model
            else:
                print(f"Please enter a number between 1 and {len(available_models)}")
        except ValueError:
            print("Please enter a valid number or press Enter for the default model")

def query_ollama(prompt, model):
    """
    Send a query to Ollama API and get a response
    """
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return "I'm having trouble connecting to my knowledge base. Let's continue anyway."
