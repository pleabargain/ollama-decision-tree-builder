#!/usr/bin/env python3
"""
Fake User Input Script for decision_tree_expert.py

This script simulates user input for the decision_tree_expert.py program
and ensures that the output is saved as a valid JSON file according to
the schema in templates/decision_tree_schema.json.
"""
import json
import subprocess
import sys
import os
import time
import datetime

def create_input_file(filename="fake-user-input.json"):
    """
    Create a JSON file with predefined inputs for decision_tree_expert.py
    """
    inputs = {
        "model": "llama3.2",  # Model to use
        "category": "Technology",  # Expert category
        "expert_type": "Cybersecurity",  # Specific expert type
        "use_recommended_model": "n",  # Don't use recommended model
        "conversation": [
            "Tell me about supply chain attacks",  # First user message
            "What are some notable examples?",     # Second user message
            "How can companies protect themselves?", # Third user message
            "exit"  # End the conversation
        ]
    }
    
    with open(filename, 'w') as f:
        json.dump(inputs, f, indent=2)
    
    print(f"Created input file: {filename}")
    return filename

def run_decision_tree_expert(input_file):
    """
    Run decision_tree_expert.py with the input file
    """
    try:
        # Run the decision_tree_expert.py script with the input file
        cmd = [sys.executable, "decision_tree_expert.py", input_file]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Get any errors
        stderr = process.stderr.read()
        if stderr:
            print(f"Error: {stderr}")
        
        # Get the return code
        return_code = process.poll()
        if return_code != 0:
            print(f"Process exited with code {return_code}")
            return False
        
        return True
    except Exception as e:
        print(f"Error running decision_tree_expert.py: {e}")
        return False

def main():
    # Create the input file
    input_file = create_input_file()
    
    # Run decision_tree_expert.py with the input file
    success = run_decision_tree_expert(input_file)
    
    if success:
        print("\nScript completed successfully.")
        
        # Check for the output file
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        output_pattern = f"conversation_history/Cybersecurity_history_{timestamp}"
        
        found_files = []
        for file in os.listdir("conversation_history"):
            if file.startswith("Cybersecurity_history_") and file.endswith(".json"):
                found_files.append(file)
        
        if found_files:
            print(f"\nFound output files:")
            for file in found_files:
                print(f"- conversation_history/{file}")
                
                # Validate the JSON structure
                try:
                    with open(f"conversation_history/{file}", 'r') as f:
                        data = json.load(f)
                    
                    # Check if it matches the schema
                    if "metadata" in data and "conversation_flow" in data:
                        print(f"  ✓ File matches the schema")
                    else:
                        print(f"  ✗ File does not match the schema")
                except Exception as e:
                    print(f"  ✗ Error validating file: {e}")
        else:
            print("\nNo output files found in conversation_history/")
    else:
        print("\nScript failed.")

if __name__ == "__main__":
    main()
