#!/usr/bin/env python3
"""
Decision Tree Conversation System for Ollama

This script implements a conversation system based on a decision tree structure.
It presents questions to the user based on the current node in the decision tree,
accepts both multiple choice and free text responses, and navigates through the tree
based on the user's responses.
"""
import json
import datetime
import time
import os
import sys
import copy
from ollama_utils import select_model, query_ollama, check_ollama_running, get_available_models

class DecisionTreeConversation:
    """
    Main class for the Decision Tree Conversation System
    """
    def __init__(self, template_path=None):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_node_id = "root"
        self.expert_type = None
        self.model = None
        self.conversation_history = []
        self.decision_tree = None
        self.template_path = template_path
        self.available_models = []
        self.commands = {
            "exit": self.exit_conversation,
            "save": self.save_conversation,
            "help": self.show_help,
            "back": self.go_back
        }
        self.templates_dir = "templates"
        self.history_dir = "conversation_history"
        
        # Create directories if they don't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)
    
    def list_files(self, directory, extension=".json"):
        """
        List all files with the given extension in the directory
        """
        if not os.path.exists(directory):
            return []
        
        return [f for f in os.listdir(directory) if f.endswith(extension)]
    
    def select_file(self, files, prompt_text):
        """
        Let the user select a file from a list
        """
        if not files:
            print(f"No files found.")
            return None
        
        print(f"\n{prompt_text}")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
        print(f"{len(files) + 1}. Enter custom path")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (number): "))
                if 1 <= choice <= len(files):
                    return files[choice - 1]
                elif choice == len(files) + 1:
                    custom_path = input("Enter the path to the file: ")
                    if os.path.exists(custom_path) and custom_path.endswith(".json"):
                        return custom_path
                    else:
                        print("Invalid file path. Please try again.")
                else:
                    print(f"Please enter a number between 1 and {len(files) + 1}")
            except ValueError:
                print("Please enter a valid number")
    
    def load_decision_tree(self, is_template=True):
        """
        Load the decision tree from a JSON file
        """
        try:
            # If no template path is provided, prompt the user to select one
            if not self.template_path:
                if is_template:
                    # Move default templates to templates directory if they exist
                    for default_template in ["decision_tree_schema.json", "decision_tree_template.json", "IT_career_decision_tree_20250330.json"]:
                        if os.path.exists(default_template) and not os.path.exists(os.path.join(self.templates_dir, default_template)):
                            os.rename(default_template, os.path.join(self.templates_dir, default_template))
                    
                    # List available templates
                    template_files = self.list_files(self.templates_dir)
                    
                    # If no templates found, use the schema as default
                    if not template_files and os.path.exists("decision_tree_schema.json"):
                        self.template_path = "decision_tree_schema.json"
                    else:
                        selected_file = self.select_file(template_files, "Select a template:")
                        if selected_file:
                            if os.path.isabs(selected_file):
                                self.template_path = selected_file
                            else:
                                self.template_path = os.path.join(self.templates_dir, selected_file)
                        else:
                            # Default to schema if available, otherwise template
                            if os.path.exists(os.path.join(self.templates_dir, "decision_tree_schema.json")):
                                self.template_path = os.path.join(self.templates_dir, "decision_tree_schema.json")
                            elif os.path.exists(os.path.join(self.templates_dir, "decision_tree_template.json")):
                                self.template_path = os.path.join(self.templates_dir, "decision_tree_template.json")
                            else:
                                print("No templates found.")
                                return False
                else:
                    # List available conversation histories
                    history_files = self.list_files(self.history_dir)
                    selected_file = self.select_file(history_files, "Select a conversation history:")
                    if selected_file:
                        if os.path.isabs(selected_file):
                            self.template_path = selected_file
                        else:
                            self.template_path = os.path.join(self.history_dir, selected_file)
                    else:
                        print("No conversation history selected.")
                        return False
            
            # Load the file
            with open(self.template_path, 'r') as f:
                self.decision_tree = json.load(f)
                self.expert_type = self.decision_tree["metadata"]["expert_type"]
                
                # If loading a template (not a conversation history), clear the history
                if is_template:
                    self.conversation_history = []
                    self.decision_tree["conversation_history"] = []
                else:
                    # If loading a conversation history, set the conversation history and current node
                    self.conversation_history = self.decision_tree.get("conversation_history", [])
                    if self.conversation_history:
                        # Set the current node to the last node in the conversation
                        last_entry = self.conversation_history[-1]
                        if "next_node" in last_entry and last_entry["next_node"]:
                            self.current_node_id = last_entry["next_node"]
                
                return True
        except FileNotFoundError:
            print(f"Error: File {self.template_path} not found")
            return False
        except json.JSONDecodeError:
            print(f"Error: File {self.template_path} contains invalid JSON")
            return False
        except Exception as e:
            print(f"Error loading decision tree: {e}")
            return False
    
    def get_current_node(self):
        """
        Get the current node in the decision tree
        """
        for node in self.decision_tree["conversation_flow"]:
            if node["node_id"] == self.current_node_id:
                return node
        return None
    
    def display_question(self, node):
        """
        Display the question and options for the current node
        """
        print(f"\n{node['question']}")
        
        if node["question_type"] == "multiple_choice" and "options" in node:
            print("\nOptions:")
            for option in node["options"]:
                print(f"{option['option_id']}. {option['text']}")
            
            print("\nType a number to select an option, or type your own response.")
            print("Type 'help' to see available commands.")
    
    def process_response(self, response, node):
        """
        Process the user's response and determine the next node
        """
        # Check if the response is a command
        if response.lower() in self.commands:
            return self.commands[response.lower()]()
        
        # Check if the response is a valid option number
        next_node_id = None
        response_type = "free_text"
        
        if node["question_type"] == "multiple_choice" and "options" in node:
            options_presented = [option["text"] for option in node["options"]]
            
            # Check if the response is a valid option number
            if response.isdigit():
                option_id = response
                for option in node["options"]:
                    if option["option_id"] == option_id:
                        next_node_id = option["next_node"]
                        response_type = "option"
                        break
            
            # If not a valid option number, use the default next node
            if next_node_id is None and "default_next_node" in node:
                next_node_id = node["default_next_node"]
        
        # Record this interaction in the conversation history
        timestamp = datetime.datetime.now().isoformat()
        
        history_entry = {
            "timestamp": timestamp,
            "node_id": node["node_id"],
            "question": node["question"],
            "options_presented": options_presented if "options_presented" in locals() else [],
            "user_response": response,
            "response_type": response_type,
            "next_node": next_node_id
        }
        
        self.conversation_history.append(history_entry)
        self.decision_tree["conversation_history"] = self.conversation_history
        
        # Update the current node
        if next_node_id:
            self.current_node_id = next_node_id
            return True
        else:
            print("I'm not sure how to proceed with that response. Let's try a different approach.")
            return False
    
    def exit_conversation(self):
        """
        Exit the conversation
        """
        self.save_conversation()
        print("\nThank you for using the Decision Tree Conversation System. Goodbye!")
        return "exit"
    
    def save_conversation(self):
        """
        Save the conversation to a JSON file
        """
        # Create directory for conversation files if it doesn't exist
        os.makedirs("conversation_history", exist_ok=True)
        
        # Save the conversation history to a JSON file
        safe_expert_type = self.expert_type.replace(' ', '_').replace('/', '_')
        filename = f"conversation_history/{safe_expert_type}_decision_tree_{self.timestamp}.json"
        
        # Create a copy of the decision tree with the updated conversation history
        output_data = copy.deepcopy(self.decision_tree)
        output_data["conversation_history"] = self.conversation_history
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nConversation saved to {filename}")
        return True
    
    def show_help(self):
        """
        Show available commands
        """
        print("\nAvailable commands:")
        print("  help  - Show this help message")
        print("  save  - Save the conversation")
        print("  exit  - Save and exit the conversation")
        print("  back  - Go back to the previous question (if possible)")
        return True
    
    def go_back(self):
        """
        Go back to the previous question
        """
        if len(self.conversation_history) > 1:
            # Remove the last entry from the conversation history
            self.conversation_history.pop()
            
            # Set the current node to the previous node
            previous_entry = self.conversation_history[-1]
            self.current_node_id = previous_entry["node_id"]
            
            print("\nGoing back to the previous question.")
            return True
        else:
            print("\nCannot go back any further.")
            return True
    
    def generate_ollama_prompt(self, node, user_response=None):
        """
        Generate a prompt for Ollama based on the current node and conversation history
        """
        system_prompt = f"You are an expert in {self.expert_type}. Provide knowledgeable and helpful responses about {self.expert_type}."
        
        # Add context from the conversation history
        context = ""
        if self.conversation_history:
            context = "Previous conversation:\n"
            for entry in self.conversation_history:
                context += f"Question: {entry['question']}\n"
                if entry['options_presented']:
                    context += "Options: " + ", ".join(entry['options_presented']) + "\n"
                context += f"User response: {entry['user_response']}\n\n"
        
        # Add the current question and user response
        current_question = f"Current question: {node['question']}\n"
        if "options" in node:
            current_question += "Options: " + ", ".join([option['text'] for option in node['options']]) + "\n"
        
        if user_response:
            current_question += f"User response: {user_response}\n"
        
        # Construct the full prompt
        full_prompt = f"{system_prompt}\n\n{context}{current_question}\n\nProvide a thoughtful, helpful response to the user's input. If the user asked a question, answer it thoroughly. If the user selected an option, provide information relevant to that choice."
        
        return full_prompt
    
    def run(self):
        """
        Run the conversation
        """
        # Welcome message
        print("\n" + "=" * 60)
        print("Welcome to the Decision Tree Conversation System!")
        print("=" * 60)
        
        # Check if Ollama is running
        if not check_ollama_running():
            print("\nOllama must be running to use this application.")
            print("Please start Ollama and try again.")
            print("If Ollama is not installed, visit https://ollama.ai/ for installation instructions.")
            sys.exit(1)
        
        # Get available models
        self.available_models = get_available_models()
        
        if not self.available_models:
            print("\nNo models found. You need to pull models before using the system.")
            print("Example: ollama pull gemma3")
            print("Example: ollama pull llama2")
            sys.exit(1)
        
        # Ask the user what they want to do
        print("\nWhat would you like to do?")
        print("1. Start a new conversation with a template")
        print("2. Continue an existing conversation")
        
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "1":
            # Load a template
            if not self.load_decision_tree(is_template=True):
                print("Failed to load template. Exiting.")
                sys.exit(1)
        elif choice == "2":
            # Load a conversation history
            if not self.load_decision_tree(is_template=False):
                print("Failed to load conversation history. Exiting.")
                sys.exit(1)
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)
        
        # Select the Ollama model to use
        self.model = select_model(default_model="gemma3")
        
        print(f"\nLoaded decision tree for expert type: {self.expert_type}")
        print(f"Using model: {self.model}")
        
        # Main conversation loop
        try:
            while True:
                # Get the current node
                current_node = self.get_current_node()
                
                if not current_node:
                    print(f"Error: Node '{self.current_node_id}' not found in the decision tree.")
                    break
                
                # Display the question and options
                self.display_question(current_node)
                
                # Get user input
                user_input = input("\nYou: ")
                
                # Process the response
                result = self.process_response(user_input, current_node)
                
                if result == "exit":
                    break
                
                # If the user provided a free-text response that wasn't a command,
                # generate a response from Ollama
                if result and user_input.lower() not in self.commands:
                    # Generate a prompt for Ollama
                    prompt = self.generate_ollama_prompt(current_node, user_input)
                    
                    # Get response from Ollama
                    print("\nProcessing your response...")
                    response = query_ollama(prompt, self.model)
                    
                    # Display the response
                    print(f"\nExpert: {response}")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Saving conversation...")
            self.save_conversation()
            print("Goodbye!")
        
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            self.save_conversation()
            print("The conversation has been saved.")

if __name__ == "__main__":
    # Check if a file path was provided as a command-line argument
    if len(sys.argv) > 1:
        conversation = DecisionTreeConversation(template_path=sys.argv[1])
    else:
        conversation = DecisionTreeConversation()
    
    conversation.run()
