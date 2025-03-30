import json
import datetime
import time
import os
import re
import argparse
from ollama_utils import select_model, query_ollama
from color_utils import (
    print_welcome, print_system, print_header, print_error, print_expert,
    print_success, colored_input, print_separator, colored, print_options,
    print_help, format_command, SYSTEM_COLOR, OPTION_ID_COLOR, ERROR_COLOR,
    HELP_COLOR, EXPERT_COLOR
)

def save_conversation(conversation_history, expert_type, timestamp=None):
    """
    Save the conversation history to a JSON file
    """
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create directory for history files if it doesn't exist
    os.makedirs("conversation_history", exist_ok=True)
    
    # Save the conversation history to a JSON file
    safe_expert_type = expert_type.replace(' ', '_').replace('/', '_')
    filename = f"conversation_history/{safe_expert_type}_history_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(conversation_history, f, indent=2)
    
    print_success(f"\nConversation history saved to {filename}")
    return filename

def extract_options(response):
    """
    Extract multiple choice options from the response
    Returns a list of options if found, otherwise None
    """
    # Look for options in the format a) option text or a. option text
    option_pattern = r'(?:^|\n)([a-d])[).]\s+(.+?)(?=\n[a-d][).]|\n\n|\n$|$)'
    matches = re.findall(option_pattern, response, re.MULTILINE | re.DOTALL)
    
    if matches:
        return [(option[0], option[1].strip()) for option in matches]
    
    # Try another pattern for numbered options: 1. option text
    option_pattern = r'(?:^|\n)([1-4])[).]\s+(.+?)(?=\n[1-4][).]|\n\n|\n$|$)'
    matches = re.findall(option_pattern, response, re.MULTILINE | re.DOTALL)
    
    if matches:
        return [(option[0], option[1].strip()) for option in matches]
    
    return None

def show_help():
    """
    Show available commands
    """
    print_help("\nAvailable commands:")
    print_help(f"  {format_command('help')}  - Show this help message")
    print_help(f"  {format_command('save')}  - Save the conversation")
    print_help(f"  {format_command('exit')}  - Save and exit the conversation")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Ollama Expert System")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--expert", type=str, help="Specify expert type directly")
    args = parser.parse_args()
    
    # Check if colors should be disabled
    if args.no_color:
        from color_utils import disable_colors
        disable_colors()
    
    # Get current timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize conversation history
    conversation_history = []
    
    # Welcome message
    print_welcome("Welcome to the Ollama Expert System!")
    
    # Select the Ollama model to use (this will also check if Ollama is running)
    model = select_model(default_model="gemma3")
    
    # Ask the user what type of expert they want to talk to
    if args.expert:
        expert_type = args.expert
        print_system(f"\nExpert type: {expert_type}")
    else:
        expert_type = colored_input("\nWhat type of expert would you like to talk to today? ")
    
    # Create the system prompt for the expert
    system_prompt = f"""You are an expert in {expert_type}. Provide knowledgeable and helpful responses about {expert_type}.

When appropriate, present multiple choice options to the user in this format:
a) First option
b) Second option
c) Third option
d) Other (please specify)

This helps guide the conversation while still allowing for open-ended responses."""
    
    # Record this initial setup in the conversation history
    conversation_history.append({
        "role": "system",
        "content": system_prompt
    })
    
    # Initialize the expert by sending the system prompt
    print_system(f"\nInitializing {expert_type} expert...\n")
    
    # Ask one question before beginning the main conversation
    initial_prompt = f"""{system_prompt}

Ask the user one thoughtful question about {expert_type} to start the conversation. 
Present it as a multiple choice question with 3-4 options, following the format specified above.
Make sure the options are relevant and cover the main areas of interest within {expert_type}."""
    
    initial_question = query_ollama(initial_prompt, model)
    
    print_expert(initial_question)
    
    # Extract options if present
    options = extract_options(initial_question)
    if options:
        print_options(options)
    
    # Record this in the conversation history
    conversation_history.append({
        "role": "assistant",
        "content": initial_question
    })
    
    # Define commands
    commands = {
        "help": lambda: show_help(),
        "save": lambda: save_conversation(conversation_history, expert_type, timestamp),
        "exit": lambda: "exit"
    }
    
    # Show available commands
    print_system(f"\nType {format_command('help')} to see available commands.")
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = colored_input("\nYou (type a letter/number for options, or your own response): ")
        
        # Record user input in conversation history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Check if user input is a command
        if user_input.lower() in commands:
            result = commands[user_input.lower()]()
            if result == "exit":
                print_success("Thank you for using the Ollama Expert System. Goodbye!")
                break
            continue
        
        # Create the full prompt with conversation history
        full_prompt = system_prompt + "\n\n"
        for entry in conversation_history:
            if entry["role"] == "user":
                full_prompt += f"User: {entry['content']}\n"
            elif entry["role"] == "assistant":
                full_prompt += f"Expert: {entry['content']}\n"
        
        # Add instruction to include multiple choice options when appropriate
        full_prompt += """Expert: 

Remember to present multiple choice options when appropriate, using the format:
a) First option
b) Second option
etc.

Your response:
"""
        
        # Get response from Ollama with error correction
        print_system("\nProcessing your response...")
        response = query_ollama(full_prompt, model, max_retries=3)
        
        # Display the response
        print_expert(response)
        
        # Extract options if present
        options = extract_options(response)
        if options:
            print_options(options)
        
        # Record the response in conversation history
        conversation_history.append({
            "role": "assistant",
            "content": response
        })
    
    # Save the conversation history if not already saved
    save_conversation(conversation_history, expert_type, timestamp)

if __name__ == "__main__":
    main()
