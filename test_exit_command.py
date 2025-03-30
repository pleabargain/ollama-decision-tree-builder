import os
import re

def check_exit_command_code():
    """
    Check the code in ollama_expert.py to verify it prompts to save on exit
    """
    print("Checking 'exit' command implementation in code...")
    
    # Read the ollama_expert.py file
    with open("ollama_expert.py", "r") as f:
        code = f.read()
    
    # Check if the exit command prompts to save
    exit_pattern = r"if\s+result\s*==\s*['\"]exit['\"]:.*?save_choice\s*=\s*colored_input\(['\"].*?save.*?['\"]"
    exit_match = re.search(exit_pattern, code, re.DOTALL)
    
    if exit_match:
        print("SUCCESS: Exit command code prompts to save")
        print(f"Found code: {exit_match.group(0)[:100]}...")
        return True
    else:
        print("ERROR: Exit command code does not prompt to save")
        return False

def check_help_text():
    """
    Check if the help text mentions that exit will prompt to save
    """
    print("\nChecking help text...")
    
    # Read the ollama_expert.py file
    with open("ollama_expert.py", "r") as f:
        code = f.read()
    
    # Check if the help text mentions prompting to save
    help_pattern = r"['\"]exit['\"]\s*\).*?prompt.*?save"
    help_match = re.search(help_pattern, code, re.DOTALL | re.IGNORECASE)
    
    if help_match:
        print("SUCCESS: Help text mentions prompting to save")
        print(f"Found text: {help_match.group(0)[:100]}...")
        return True
    else:
        print("ERROR: Help text does not mention prompting to save")
        return False

if __name__ == "__main__":
    code_check = check_exit_command_code()
    help_check = check_help_text()
    
    if code_check and help_check:
        print("\nTest successful! The 'exit' command prompts to save.")
    else:
        print("\nTest failed! The 'exit' command implementation is incomplete.")
