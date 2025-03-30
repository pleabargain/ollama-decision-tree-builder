#!/usr/bin/env python3
"""
Launcher script for the Ollama Decision Tree Expert System
"""
import os
import sys
import subprocess
import argparse
from ollama_utils import check_ollama_running, get_available_models
from color_utils import (
    print_welcome, print_system, print_header, print_error, 
    print_success, colored_input, print_separator, colored,
    SYSTEM_COLOR, OPTION_ID_COLOR, ERROR_COLOR
)

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    """Display the main menu"""
    clear_screen()
    print("\n")
    print_welcome("Ollama Decision Tree Expert System Launcher")
    
    print_system("\nChoose a script to run:")
    options = [
        ("1", "Basic Expert System (ollama_expert.py)"),
        ("2", "Decision Tree Expert System (decision_tree_expert.py)"),
        ("3", "Custom Decision Tree Expert System (custom_decision_tree.py)"),
        ("4", "JSON-based Decision Tree Conversation (decision_tree_conversation.py)"),
        ("5", "Test Decision Tree System (test_decision_tree.py)"),
        ("6", "Exit")
    ]
    
    for option_id, option_text in options:
        print(f"{colored(option_id, OPTION_ID_COLOR)}. {option_text}")
    
    while True:
        try:
            choice = int(colored_input("\nEnter your choice (1-6): "))
            if 1 <= choice <= 6:
                return choice
            else:
                print_error("Please enter a number between 1 and 6")
        except ValueError:
            print_error("Please enter a valid number")

def check_requirements():
    """Check if required packages are installed"""
    try:
        import requests
        return True
    except ImportError:
        print_error("The 'requests' package is required but not installed.")
        install = colored_input("Would you like to install it now? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            return True
        else:
            return False

def run_script(script_name):
    """Run the selected Python script"""
    try:
        print_system(f"\nLaunching {script_name}...\n")
        subprocess.run([sys.executable, script_name])
    except Exception as e:
        print_error(f"Error running {script_name}: {e}")
    
    colored_input("\nPress Enter to return to the menu...")

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Ollama Decision Tree Expert System Launcher")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    args = parser.parse_args()
    
    # Check if colors should be disabled
    if args.no_color:
        from color_utils import disable_colors
        disable_colors()
    
    if not check_requirements():
        print_error("Required packages are not installed. Exiting.")
        return
    
    # Check if Ollama is running
    if not check_ollama_running():
        print_error("\nOllama must be running to use this application.")
        print_system("Please start Ollama and try again.")
        print_system("If Ollama is not installed, visit https://ollama.ai/ for installation instructions.")
        return
    
    # Check if any models are available
    available_models = get_available_models()
    if not available_models:
        print_error("\nNo Ollama models found. You need to pull models before using the expert system.")
        print_system("Example: ollama pull gemma3")
        print_system("Example: ollama pull llama2")
        return
    
    print_success(f"\nFound {len(available_models)} available Ollama models: {', '.join(available_models)}")
    
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
            print_success("\nExiting. Goodbye!")
            break

if __name__ == "__main__":
    main()
