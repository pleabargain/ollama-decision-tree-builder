#!/usr/bin/env python3
"""
Launcher script for the Ollama Decision Tree Expert System
"""
import os
import sys
import subprocess
from ollama_utils import check_ollama_running, get_available_models

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    """Display the main menu"""
    clear_screen()
    print("\n" + "=" * 50)
    print("Ollama Decision Tree Expert System Launcher")
    print("=" * 50)
    print("\nChoose a script to run:")
    print("1. Basic Expert System (ollama_expert.py)")
    print("2. Decision Tree Expert System (decision_tree_expert.py)")
    print("3. Custom Decision Tree Expert System (custom_decision_tree.py)")
    print("4. JSON-based Decision Tree Conversation (decision_tree_conversation.py)")
    print("5. Test Decision Tree System (test_decision_tree.py)")
    print("6. Exit")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-6): "))
            if 1 <= choice <= 6:
                return choice
            else:
                print("Please enter a number between 1 and 6")
        except ValueError:
            print("Please enter a valid number")

def check_requirements():
    """Check if required packages are installed"""
    try:
        import requests
        return True
    except ImportError:
        print("The 'requests' package is required but not installed.")
        install = input("Would you like to install it now? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            return True
        else:
            return False

def run_script(script_name):
    """Run the selected Python script"""
    try:
        subprocess.run([sys.executable, script_name])
    except Exception as e:
        print(f"Error running {script_name}: {e}")
    
    input("\nPress Enter to return to the menu...")

def main():
    """Main function"""
    if not check_requirements():
        print("Required packages are not installed. Exiting.")
        return
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("\nOllama must be running to use this application.")
        print("Please start Ollama and try again.")
        print("If Ollama is not installed, visit https://ollama.ai/ for installation instructions.")
        return
    
    # Check if any models are available
    available_models = get_available_models()
    if not available_models:
        print("\nNo Ollama models found. You need to pull models before using the expert system.")
        print("Example: ollama pull gemma3")
        print("Example: ollama pull llama2")
        return
    
    print(f"\nFound {len(available_models)} available Ollama models: {', '.join(available_models)}")
    
    while True:
        choice = display_menu()
        
        if choice == 1:
            run_script("ollama_expert.py")
        elif choice == 2:
            run_script("decision_tree_expert.py")
        elif choice == 3:
            run_script("custom_decision_tree.py")
        elif choice == 4:
            run_script("decision_tree_conversation.py")
        elif choice == 5:
            run_script("test_decision_tree.py")
        elif choice == 6:
            print("\nExiting. Goodbye!")
            break

if __name__ == "__main__":
    main()
