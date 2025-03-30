import json
import datetime
import time
import os
from ollama_utils import select_model, query_ollama

def main():
    # Get current timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize conversation history
    conversation_history = []
    
    # Welcome message
    print("\n" + "=" * 50)
    print("Welcome to the Ollama Expert System!")
    print("=" * 50)
    
    # Select the Ollama model to use (this will also check if Ollama is running)
    model = select_model(default_model="gemma3")
    
    # Ask the user what type of expert they want to talk to
    expert_type = input("\nWhat type of expert would you like to talk to today? ")
    
    # Create the system prompt for the expert
    system_prompt = f"You are an expert in {expert_type}. Provide knowledgeable and helpful responses about {expert_type}."
    
    # Record this initial setup in the conversation history
    conversation_history.append({
        "role": "system",
        "content": system_prompt
    })
    
    # Initialize the expert by sending the system prompt
    print(f"\nInitializing {expert_type} expert...\n")
    
    # Ask one question before beginning the main conversation
    initial_question = query_ollama(
        f"{system_prompt}\n\nAsk the user one thoughtful question about {expert_type} to start the conversation.",
        model
    )
    
    print(f"Expert: {initial_question}")
    
    # Record this in the conversation history
    conversation_history.append({
        "role": "assistant",
        "content": initial_question
    })
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("\nYou (type 'exit' to end): ")
        
        # Record user input in conversation history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Check if user wants to exit
        if user_input.lower() == 'exit':
            print("Thank you for using the Ollama Expert System. Goodbye!")
            break
        
        # Create the full prompt with conversation history
        full_prompt = system_prompt + "\n\n"
        for entry in conversation_history:
            if entry["role"] == "user":
                full_prompt += f"User: {entry['content']}\n"
            elif entry["role"] == "assistant":
                full_prompt += f"Expert: {entry['content']}\n"
        
        full_prompt += "Expert: "
        
        # Get response from Ollama
        response = query_ollama(full_prompt, model)
        
        # Display the response
        print(f"\nExpert: {response}")
        
        # Record the response in conversation history
        conversation_history.append({
            "role": "assistant",
            "content": response
        })
    
    # Create directory for history files if it doesn't exist
    os.makedirs("conversation_history", exist_ok=True)
    
    # Save the conversation history to a JSON file
    safe_expert_type = expert_type.replace(' ', '_').replace('/', '_')
    filename = f"conversation_history/{safe_expert_type}_history_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(conversation_history, f, indent=2)
    
    print(f"\nConversation history saved to {filename}")

if __name__ == "__main__":
    main()
