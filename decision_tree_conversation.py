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
import logging
import traceback
from ollama_utils import select_model, query_ollama, check_ollama_running, get_available_models

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("decision_tree_conversation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("decision_tree")

class DecisionTreeConversation:
    """
    Main class for the Decision Tree Conversation System
    """
    def __init__(self, template_path=None, test_mode=False):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_node_id = "root"
        self.expert_type = None
        self.model = None
        self.conversation_history = []
        self.decision_tree = None
        self.template_path = template_path
        self.available_models = []
        self.test_mode = test_mode
        self.error_count = 0
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
        
        logger.info("DecisionTreeConversation initialized")
        if test_mode:
            logger.info("Running in test mode")
    
    def list_files(self, directory, extension=".json"):
        """
        List all files with the given extension in the directory
        """
        try:
            if not os.path.exists(directory):
                logger.warning(f"Directory {directory} does not exist")
                return []
            
            files = [f for f in os.listdir(directory) if f.endswith(extension)]
            logger.debug(f"Found {len(files)} files in {directory}")
            return files
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []
    
    def select_file(self, files, prompt_text):
        """
        Let the user select a file from a list
        """
        if not files:
            logger.warning("No files found for selection")
            print(f"No files found.")
            return None
        
        print(f"\n{prompt_text}")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
        print(f"{len(files) + 1}. Enter custom path")
        
        while True:
            try:
                if self.test_mode:
                    # In test mode, always select the first file
                    choice = 1
                else:
                    choice = int(input("\nEnter your choice (number): "))
                
                if 1 <= choice <= len(files):
                    selected_file = files[choice - 1]
                    logger.info(f"Selected file: {selected_file}")
                    return selected_file
                elif choice == len(files) + 1:
                    custom_path = input("Enter the path to the file: ")
                    if os.path.exists(custom_path) and custom_path.endswith(".json"):
                        logger.info(f"Selected custom path: {custom_path}")
                        return custom_path
                    else:
                        logger.warning(f"Invalid file path: {custom_path}")
                        print("Invalid file path. Please try again.")
                else:
                    logger.warning(f"Invalid choice: {choice}")
                    print(f"Please enter a number between 1 and {len(files) + 1}")
            except ValueError:
                logger.warning("Invalid input (not a number)")
                print("Please enter a valid number")
    
    def validate_json_structure(self, data):
        """
        Validate that the JSON data has the required structure
        """
        try:
            # Check if this is a list (old format)
            if isinstance(data, list):
                return True, "Old format, will be converted"
            
            # Check for required fields
            required_fields = ["metadata", "conversation_flow"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False, f"Missing required field: {field}"
            
            # Check metadata
            if "expert_type" not in data["metadata"]:
                logger.error("Missing expert_type in metadata")
                return False, "Missing expert_type in metadata"
            
            # Check conversation flow
            if not isinstance(data["conversation_flow"], list):
                logger.error("conversation_flow must be a list")
                return False, "conversation_flow must be a list"
            
            # Check for root node
            root_node = None
            for node in data["conversation_flow"]:
                if "node_id" not in node:
                    logger.error("Node missing node_id")
                    return False, "Node missing node_id"
                
                if node["node_id"] == "root":
                    root_node = node
            
            if not root_node:
                logger.error("Missing root node")
                return False, "Missing root node"
            
            # Check conversation history if present
            if "conversation_history" in data:
                if not isinstance(data["conversation_history"], list):
                    logger.error("conversation_history must be a list")
                    return False, "conversation_history must be a list"
            
            return True, "Valid JSON structure"
        except Exception as e:
            logger.error(f"Error validating JSON structure: {e}")
            return False, f"Error validating JSON structure: {e}"
    
    def convert_conversation_format(self, data):
        """
        Convert different conversation history formats to the expected format
        """
        try:
            # If the conversation history is in the ollama_expert.py format
            if isinstance(data, list):
                logger.info("Converting from ollama_expert.py format")
                
                # Create a new structure
                converted_data = {
                    "metadata": {
                        "title": "Converted Conversation",
                        "version": "1.0",
                        "created_at": datetime.datetime.now().isoformat(),
                        "expert_type": "unknown"
                    },
                    "conversation_flow": [
                        {
                            "node_id": "root",
                            "question": "What would you like to talk about?",
                            "question_type": "open",
                            "default_next_node": "root"
                        }
                    ],
                    "conversation_history": []
                }
                
                # Extract expert type from system prompt if available
                for entry in data:
                    if entry.get("role") == "system":
                        content = entry.get("content", "")
                        if "expert in" in content:
                            expert_type = content.split("expert in")[1].split(".")[0].strip()
                            converted_data["metadata"]["expert_type"] = expert_type
                
                # Convert conversation entries
                for i, entry in enumerate(data):
                    if entry.get("role") == "user":
                        # Find the next assistant response
                        assistant_response = ""
                        for j in range(i+1, len(data)):
                            if data[j].get("role") == "assistant":
                                assistant_response = data[j].get("content", "")
                                break
                        
                        # Add to conversation history
                        history_entry = {
                            "timestamp": datetime.datetime.now().isoformat(),
                            "node_id": "root",
                            "question": "What would you like to talk about?",
                            "options_presented": [],
                            "user_response": entry.get("content", ""),
                            "response_type": "free_text",
                            "next_node": "root",
                            "assistant_response": assistant_response
                        }
                        converted_data["conversation_history"].append(history_entry)
                
                return converted_data
            
            return data
        except Exception as e:
            logger.error(f"Error converting conversation format: {e}")
            return data
    
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
                            logger.info(f"Moving {default_template} to {self.templates_dir}")
                            os.rename(default_template, os.path.join(self.templates_dir, default_template))
                    
                    # List available templates
                    template_files = self.list_files(self.templates_dir)
                    
                    # If no templates found, use the schema as default
                    if not template_files and os.path.exists("decision_tree_schema.json"):
                        logger.info("Using decision_tree_schema.json as default")
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
                                logger.info("Using decision_tree_schema.json as default")
                                self.template_path = os.path.join(self.templates_dir, "decision_tree_schema.json")
                            elif os.path.exists(os.path.join(self.templates_dir, "decision_tree_template.json")):
                                logger.info("Using decision_tree_template.json as default")
                                self.template_path = os.path.join(self.templates_dir, "decision_tree_template.json")
                            else:
                                logger.error("No templates found")
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
                        logger.error("No conversation history selected")
                        print("No conversation history selected.")
                        return False
            
            logger.info(f"Loading file: {self.template_path}")
            
            # Load the file
            with open(self.template_path, 'r') as f:
                data = json.load(f)
            
            # Convert format if needed
            data = self.convert_conversation_format(data)
            
            # Validate the structure
            valid, message = self.validate_json_structure(data)
            if not valid:
                logger.error(f"Invalid JSON structure: {message}")
                print(f"Error: {message}")
                return False
            
            self.decision_tree = data
            self.expert_type = self.decision_tree["metadata"]["expert_type"]
            logger.info(f"Loaded decision tree for expert type: {self.expert_type}")
            
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
                        logger.info(f"Set current node to: {self.current_node_id}")
            
            return True
        except FileNotFoundError:
            logger.error(f"File not found: {self.template_path}")
            print(f"Error: File {self.template_path} not found")
            return False
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in file: {self.template_path}")
            print(f"Error: File {self.template_path} contains invalid JSON")
            return False
        except Exception as e:
            logger.error(f"Error loading decision tree: {e}")
            logger.error(traceback.format_exc())
            print(f"Error loading decision tree: {e}")
            return False
    
    def get_current_node(self):
        """
        Get the current node in the decision tree
        """
        try:
            for node in self.decision_tree["conversation_flow"]:
                if node["node_id"] == self.current_node_id:
                    return node
            
            logger.error(f"Node not found: {self.current_node_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting current node: {e}")
            return None
    
    def display_question(self, node):
        """
        Display the question and options for the current node
        """
        try:
            print(f"\n{node['question']}")
            
            if node["question_type"] == "multiple_choice" and "options" in node:
                print("\nOptions:")
                for option in node["options"]:
                    print(f"{option['option_id']}. {option['text']}")
                
                print("\nType a number to select an option, or type your own response.")
                print("Type 'help' to see available commands.")
        except Exception as e:
            logger.error(f"Error displaying question: {e}")
            print("Error displaying question. Please try again.")
    
    def process_response(self, response, node):
        """
        Process the user's response and determine the next node
        """
        try:
            # Check if the response is a command
            if response.lower() in self.commands:
                logger.info(f"Processing command: {response.lower()}")
                return self.commands[response.lower()]()
            
            # Check if the response is a valid option number
            next_node_id = None
            response_type = "free_text"
            options_presented = []
            
            if node["question_type"] == "multiple_choice" and "options" in node:
                options_presented = [option["text"] for option in node["options"]]
                
                # Check if the response is a valid option number
                if response.isdigit():
                    option_id = response
                    for option in node["options"]:
                        if option["option_id"] == option_id:
                            next_node_id = option["next_node"]
                            response_type = "option"
                            logger.info(f"Selected option {option_id}, next node: {next_node_id}")
                            break
                
                # If not a valid option number, use the default next node
                if next_node_id is None and "default_next_node" in node:
                    next_node_id = node["default_next_node"]
                    logger.info(f"Using default next node: {next_node_id}")
            elif "default_next_node" in node:
                next_node_id = node["default_next_node"]
                logger.info(f"Using default next node: {next_node_id}")
            
            # Record this interaction in the conversation history
            timestamp = datetime.datetime.now().isoformat()
            
            history_entry = {
                "timestamp": timestamp,
                "node_id": node["node_id"],
                "question": node["question"],
                "options_presented": options_presented,
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
                logger.warning(f"No next node found for response: {response}")
                print("I'm not sure how to proceed with that response. Let's try a different approach.")
                return False
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            logger.error(traceback.format_exc())
            print(f"Error processing response: {e}")
            return False
    
    def exit_conversation(self):
        """
        Exit the conversation
        """
        try:
            logger.info("Exiting conversation")
            self.save_conversation()
            print("\nThank you for using the Decision Tree Conversation System. Goodbye!")
            return "exit"
        except Exception as e:
            logger.error(f"Error exiting conversation: {e}")
            print(f"Error exiting conversation: {e}")
            return "exit"
    
    def save_conversation(self):
        """
        Save the conversation to a JSON file
        """
        try:
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
            
            logger.info(f"Conversation saved to {filename}")
            print(f"\nConversation saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            print(f"Error saving conversation: {e}")
            return False
    
    def show_help(self):
        """
        Show available commands
        """
        try:
            logger.info("Showing help")
            print("\nAvailable commands:")
            print("  help  - Show this help message")
            print("  save  - Save the conversation")
            print("  exit  - Save and exit the conversation")
            print("  back  - Go back to the previous question (if possible)")
            return True
        except Exception as e:
            logger.error(f"Error showing help: {e}")
            print(f"Error showing help: {e}")
            return False
    
    def go_back(self):
        """
        Go back to the previous question
        """
        try:
            if len(self.conversation_history) > 1:
                # Remove the last entry from the conversation history
                self.conversation_history.pop()
                
                # Set the current node to the previous node
                previous_entry = self.conversation_history[-1]
                self.current_node_id = previous_entry["node_id"]
                
                logger.info(f"Going back to node: {self.current_node_id}")
                print("\nGoing back to the previous question.")
                return True
            else:
                logger.info("Cannot go back any further")
                print("\nCannot go back any further.")
                return True
        except Exception as e:
            logger.error(f"Error going back: {e}")
            print(f"Error going back: {e}")
            return False
    
    def generate_ollama_prompt(self, node, user_response=None):
        """
        Generate a prompt for Ollama based on the current node and conversation history
        """
        try:
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
        except Exception as e:
            logger.error(f"Error generating Ollama prompt: {e}")
            return f"You are an expert in {self.expert_type}. The user asked: {user_response}"
    
    def start_conversation(self):
        """
        Start the conversation loop
        """
        try:
            logger.info("Starting conversation")
            
            # Main conversation loop
            while True:
                # Get the current node
                current_node = self.get_current_node()
                
                if not current_node:
                    logger.error(f"Node '{self.current_node_id}' not found in the decision tree")
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
            logger.info("Conversation interrupted by user")
            print("\n\nInterrupted by user. Saving conversation...")
            self.save_conversation()
            print("Goodbye!")
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
            logger.error(traceback.format_exc())
            print(f"\nAn error occurred: {e}")
            self.save_conversation()
            print("The conversation has been saved.")
    
    def run_tests(self):
        """
        Run tests on the decision tree conversation system
        """
        try:
            print("\n" + "=" * 60)
            print("Running Decision Tree Conversation System Tests")
            print("=" * 60)
            
            test_results = []
            
            # Test 1: Validate template files
            print("\nTest 1: Validating template files...")
            template_files = self.list_files(self.templates_dir)
            for template_file in template_files:
                try:
                    with open(os.path.join(self.templates_dir, template_file), 'r') as f:
                        data = json.load(f)
                    
                    valid, message = self.validate_json_structure(data)
                    if valid:
                        print(f"  ✓ {template_file} is valid")
                        test_results.append(("Template validation: " + template_file, "PASS"))
                    else:
                        print(f"  ✗ {template_file} is invalid: {message}")
                        test_results.append(("Template validation: " + template_file, "FAIL", message))
                except Exception as e:
                    print(f"  ✗ Error validating {template_file}: {e}")
                    test_results.append(("Template validation: " + template_file, "ERROR", str(e)))
            
            # Test 2: Validate conversation history files
            print("\nTest 2: Validating conversation history files...")
            history_files = self.list_files(self.history_dir)
            for history_file in history_files:
                try:
                    with open(os.path.join(self.history_dir, history_file), 'r') as f:
                        data = json.load(f)
                    
                    # Try to convert the format if needed
                    data = self.convert_conversation_format(data)
                    
                    valid, message = self.validate_json_structure(data)
                    if valid:
                        print(f"  ✓ {history_file} is valid or can be converted")
                        test_results.append(("History validation: " + history_file, "PASS"))
                    else:
                        print(f"  ✗ {history_file} is invalid: {message}")
                        test_results.append(("History validation: " + history_file, "FAIL", message))
                except Exception as e:
                    print(f"  ✗ Error validating {history_file}: {e}")
                    test_results.append(("History validation: " + history_file, "ERROR", str(e)))
            
            # Test 3: Test node navigation
            print("\nTest 3: Testing node navigation...")
            if template_files:
                try:
                    # Load the first template
                    self.template_path = os.path.join(self.templates_dir, template_files[0])
                    if self.load_decision_tree(is_template=True):
                        # Get the root node
                        root_node = self.get_current_node()
                        if root_node:
                            print(f"  ✓ Root node found: {root_node['node_id']}")
                            test_results.append(("Node navigation: root node", "PASS"))
                            
                            # Test navigation to another node
                            if root_node["question_type"] == "multiple_choice" and "options" in root_node:
                                option = root_node["options"][0]
                                next_node_id = option["next_node"]
                                
                                # Simulate selecting this option
                                self.process_response(option["option_id"], root_node)
                                
                                # Check if we navigated to the correct node
                                if self.current_node_id == next_node_id:
                                    print(f"  ✓ Navigation to {next_node_id} successful")
                                    test_results.append(("Node navigation: option selection", "PASS"))
                                else:
                                    print(f"  ✗ Navigation failed: expected {next_node_id}, got {self.current_node_id}")
                                    test_results.append(("Node navigation: option selection", "FAIL", f"Expected {next_node_id}, got {self.current_node_id}"))
                        else:
                            print("  ✗ Root node not found")
                            test_results.append(("Node navigation: root node", "FAIL", "Root node not found"))
                    else:
                        print("  ✗ Failed to load template")
                        test_results.append(("Node navigation", "FAIL", "Failed to load template"))
                except Exception as e:
                    print(f"  ✗ Error testing node navigation: {e}")
                    test_results.append(("Node navigation", "ERROR", str(e)))
            else:
                print("  ✗ No templates available for testing")
                test_results.append(("Node navigation", "SKIP", "No templates available"))
            
            # Print test summary
            print("\nTest Summary:")
            print("=" * 60)
            passed = sum(1 for result in test_results if result[1] == "PASS")
            failed = sum(1 for result in test_results if result[1] == "FAIL")
            errors = sum(1 for result in test_results if result[1] == "ERROR")
            skipped = sum(1 for result in test_results if result[1] == "SKIP")
            
            print(f"Passed: {passed}")
            print(f"Failed: {failed}")
            print(f"Errors: {errors}")
            print(f"Skipped: {skipped}")
            print(f"Total: {len(test_results)}")
            
            if failed == 0 and errors == 0:
                print("\nAll tests passed!")
            else:
                print("\nSome tests failed or had errors. See log for details.")
            
            # Log detailed results
            logger.info("Test results:")
            for result in test_results:
                if result[1] == "PASS":
                    logger.info(f"PASS: {result[0]}")
                elif result[1] == "FAIL":
                    logger.error(f"FAIL: {result[0]} - {result[2]}")
                elif result[1] == "ERROR":
                    logger.error(f"ERROR: {result[0]} - {result[2]}")
                elif result[1] == "SKIP":
                    logger.warning(f"SKIP: {result[0]} - {result[2]}")
            
            input("\nPress Enter to return to the main menu...")
            return True
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            logger.error(traceback.format_exc())
            print(f"Error running tests: {e}")
            input("\nPress Enter to return to the main menu...")
            return False
    
    def run(self):
        """
        Run the conversation
        """
        try:
            # Welcome message
            print("\n" + "=" * 60)
            print("Welcome to the Decision Tree Conversation System!")
            print("=" * 60)
            
            # Check if Ollama is running
            if not check_ollama_running():
                logger.error("Ollama is not running")
                print("\nOllama must be running to use this application.")
                print("Please start Ollama and try again.")
                print("If Ollama is not installed, visit https://ollama.ai/ for installation instructions.")
                sys.exit(1)
            
            # Get available models
            self.available_models = get_available_models()
            
            if not self.available_models:
                logger.error("No models found")
                print("\nNo models found. You need to pull models before using the system.")
                print("Example: ollama pull gemma3")
                print("Example: ollama pull llama2")
                sys.exit(1)
            
            # Ask the user what they want to do
            print("\nWhat would you like to do?")
            print("1. Start a new conversation with a template")
            print("2. Continue an existing conversation")
            print("3. Test the script")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                # Load a template
                if not self.load_decision_tree(is_template=True):
                    logger.error("Failed to load template")
                    print("Failed to load template. Exiting.")
                    sys.exit(1)
                
                # Select the Ollama model to use
                self.model = select_model(default_model="gemma3")
                
                print(f"\nLoaded decision tree for expert type: {self.expert_type}")
                print(f"Using model: {self.model}")
                
                # Start the conversation
                self.start_conversation()
            elif choice == "2":
                # Load a conversation history
                if not self.load_decision_tree(is_template=False):
                    logger.error("Failed to load conversation history")
                    print("Failed to load conversation history. Exiting.")
                    sys.exit(1)
                
                # Select the Ollama model to use
                self.model = select_model(default_model="gemma3")
                
                print(f"\nLoaded decision tree for expert type: {self.expert_type}")
                print(f"Using model: {self.model}")
                
                # Start the conversation
                self.start_conversation()
            elif choice == "3":
                # Run tests
                logger.info("Running tests")
                self.run_tests()
            else:
                logger.error(f"Invalid choice: {choice}")
                print("Invalid choice. Exiting.")
                sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Program interrupted by user")
            print("\n\nInterrupted by user. Exiting.")
        except Exception as e:
            logger.error(f"Error in run: {e}")
            logger.error(traceback.format_exc())
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    # Check if a file path was provided as a command-line argument
    if len(sys.argv) > 1:
        conversation = DecisionTreeConversation(template_path=sys.argv[1])
    else:
        conversation = DecisionTreeConversation()
    
    conversation.run()
