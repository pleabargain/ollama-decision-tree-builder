import json
import datetime
import time
import os
from ollama_utils import select_model, query_ollama, get_available_models

def display_menu(options, title):
    """
    Display a menu of options and get user selection
    """
    print(f"\n{title}")
    print("=" * len(title))
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")

def get_expert_categories():
    """
    Define the expert categories and their specific expert types
    """
    return {
        "Technology": [
            "Python Programming",
            "Web Development",
            "Data Science",
            "Machine Learning",
            "Cybersecurity"
        ],
        "Science": [
            "Physics",
            "Chemistry",
            "Biology",
            "Astronomy",
            "Environmental Science"
        ],
        "Business": [
            "Marketing",
            "Finance",
            "Entrepreneurship",
            "Project Management",
            "Human Resources"
        ],
        "Arts & Humanities": [
            "Literature",
            "History",
            "Philosophy",
            "Music",
            "Visual Arts"
        ],
        "Health & Wellness": [
            "Nutrition",
            "Fitness",
            "Mental Health",
            "Medicine",
            "Alternative Medicine"
        ]
    }

def get_model_for_expert(expert_type, available_models):
    """
    Determine which Ollama model to use based on expert type
    Default to gemma3 but use more specialized models if available
    """
    # This could be expanded with more model mappings
    model_mapping = {
        "Python Programming": "codellama",
        "Web Development": "codellama",
        "Data Science": "gemma3",
        "Machine Learning": "gemma3",
        # Add more mappings as needed
    }
    
    # Get the recommended model for this expert type
    recommended_model = model_mapping.get(expert_type, "gemma3")
    
    # Check if the recommended model is available
    if recommended_model in available_models:
        return recommended_model
    else:
        # If not available, use the first available model
        return available_models[0] if available_models else "gemma3"

def create_system_prompt(expert_type):
    """
    Create a detailed system prompt for the expert
    """
    return f"""You are an expert in {expert_type}. 
Provide knowledgeable, accurate, and helpful responses about {expert_type}.
Use examples and clear explanations in your answers.
If you're unsure about something, acknowledge the limitations of your knowledge.
Maintain a professional and educational tone throughout the conversation."""

def main():
    # Get current timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize conversation history
    conversation_history = []
    
    # Welcome message
    print("\n" + "=" * 50)
    print("Welcome to the Ollama Expert Decision Tree System!")
    print("=" * 50)
    
    # Check if Ollama is running and get available models
    # This will exit if Ollama is not running
    default_model = select_model(default_model="gemma3")
    available_models = get_available_models()
    
    # Get expert categories
    expert_categories = get_expert_categories()
    
    # First level: Select category
    category = display_menu(list(expert_categories.keys()), "Select an Expert Category")
    
    # Second level: Select specific expert type
    expert_type = display_menu(expert_categories[category], f"Select a {category} Expert")
    
    # Determine which model to use
    model = get_model_for_expert(expert_type, available_models)
    
    # Confirm model selection with user
    print(f"\nRecommended model for {expert_type}: {model}")
    use_recommended = input("Use this model? (y/n, default: y): ").lower() != 'n'
    
    if not use_recommended:
        model = select_model(default_model=model)
    
    # Create the system prompt for the expert
    system_prompt = create_system_prompt(expert_type)
    
    # Record this initial setup in the conversation history
    conversation_history.append({
        "role": "system",
        "content": system_prompt
    })
    
    # Initialize the expert by sending the system prompt
    print(f"\nInitializing {expert_type} expert using {model} model...\n")
    
    # Ask one question before beginning the main conversation
    initial_question_prompt = f"{system_prompt}\n\nAsk the user one thoughtful question about {expert_type} to start the conversation. Make it engaging and specific to the field."
    initial_question = query_ollama(initial_question_prompt, model)
    
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
            print("\nThank you for using the Ollama Expert System. Goodbye!")
            break
        
        # Create the full prompt with conversation history
        full_prompt = system_prompt + "\n\n"
        
        # Include the last few exchanges to keep context but avoid token limits
        recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        
        for entry in recent_history:
            if entry["role"] == "user":
                full_prompt += f"User: {entry['content']}\n"
            elif entry["role"] == "assistant" and entry["role"] != "system":
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
