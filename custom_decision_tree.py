#!/usr/bin/env python3
"""
Custom Decision Tree Expert System for Ollama
"""
import json
import datetime
import time
import os
import sys
from ollama_utils import select_model, query_ollama, get_available_models, check_ollama_running

class DecisionTreeNode:
    """
    Represents a node in the decision tree
    """
    def __init__(self, name, is_leaf=False, model=None, system_prompt=None):
        self.name = name
        self.children = []
        self.is_leaf = is_leaf
        self.model = model
        self.system_prompt = system_prompt
    
    def add_child(self, child_node):
        """Add a child node to this node"""
        self.children.append(child_node)
        return child_node
    
    def to_dict(self):
        """Convert the node to a dictionary for JSON serialization"""
        return {
            "name": self.name,
            "is_leaf": self.is_leaf,
            "model": self.model,
            "system_prompt": self.system_prompt,
            "children": [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a node from a dictionary"""
        node = cls(
            name=data["name"],
            is_leaf=data["is_leaf"],
            model=data["model"],
            system_prompt=data["system_prompt"]
        )
        for child_data in data["children"]:
            node.add_child(cls.from_dict(child_data))
        return node


class OllamaExpertSystem:
    """
    Main class for the Ollama Expert System with custom decision trees
    """
    def __init__(self):
        self.conversation_history = []
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.root = None
        self.expert_type = None
        self.model = None
        self.system_prompt = None
        self.available_models = []
    
    def display_menu(self, options, title):
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
                    return choice - 1
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
    
    def navigate_tree(self, node):
        """
        Navigate through the decision tree
        """
        current_node = node
        
        while not current_node.is_leaf:
            if not current_node.children:
                print("Error: Non-leaf node has no children!")
                return None
            
            options = [child.name for child in current_node.children]
            choice = self.display_menu(options, f"Select a {current_node.name}")
            current_node = current_node.children[choice]
        
        return current_node
    
    def create_default_tree(self):
        """
        Create a default decision tree
        """
        root = DecisionTreeNode("Expert Category")
        
        # Default model to use if recommended model is not available
        default_model = "gemma3" if "gemma3" in self.available_models else self.available_models[0]
        
        # Technology category
        tech = root.add_child(DecisionTreeNode("Technology"))
        tech.add_child(DecisionTreeNode(
            "Python Programming", 
            is_leaf=True, 
            model="codellama" if "codellama" in self.available_models else default_model,
            system_prompt="You are an expert Python programmer. Provide knowledgeable, accurate, and helpful responses about Python programming. Include code examples when appropriate."
        ))
        tech.add_child(DecisionTreeNode(
            "Web Development", 
            is_leaf=True, 
            model="codellama" if "codellama" in self.available_models else default_model,
            system_prompt="You are an expert in Web Development. Provide knowledgeable, accurate, and helpful responses about HTML, CSS, JavaScript, and web frameworks."
        ))
        tech.add_child(DecisionTreeNode(
            "Data Science", 
            is_leaf=True, 
            model=default_model,
            system_prompt="You are an expert in Data Science. Provide knowledgeable, accurate, and helpful responses about data analysis, visualization, and statistical methods."
        ))
        
        # Science category
        science = root.add_child(DecisionTreeNode("Science"))
        science.add_child(DecisionTreeNode(
            "Physics", 
            is_leaf=True, 
            model=default_model,
            system_prompt="You are an expert in Physics. Provide knowledgeable, accurate, and helpful responses about physics concepts, theories, and applications."
        ))
        science.add_child(DecisionTreeNode(
            "Biology", 
            is_leaf=True, 
            model=default_model,
            system_prompt="You are an expert in Biology. Provide knowledgeable, accurate, and helpful responses about biological systems, organisms, and processes."
        ))
        
        # Business category
        business = root.add_child(DecisionTreeNode("Business"))
        business.add_child(DecisionTreeNode(
            "Marketing", 
            is_leaf=True, 
            model=default_model,
            system_prompt="You are an expert in Marketing. Provide knowledgeable, accurate, and helpful responses about marketing strategies, consumer behavior, and brand development."
        ))
        business.add_child(DecisionTreeNode(
            "Finance", 
            is_leaf=True, 
            model=default_model,
            system_prompt="You are an expert in Finance. Provide knowledgeable, accurate, and helpful responses about financial planning, investment strategies, and economic principles."
        ))
        
        return root
    
    def create_custom_tree(self):
        """
        Guide the user through creating a custom decision tree
        """
        print("\nCreating a custom decision tree")
        print("===============================")
        
        root = DecisionTreeNode("Root")
        
        # Get the number of main categories
        while True:
            try:
                num_categories = int(input("\nHow many main categories do you want? "))
                if num_categories > 0:
                    break
                else:
                    print("Please enter a positive number")
            except ValueError:
                print("Please enter a valid number")
        
        # Create each category
        for i in range(num_categories):
            category_name = input(f"\nName for category {i+1}: ")
            category = root.add_child(DecisionTreeNode(category_name))
            
            # Get the number of experts in this category
            while True:
                try:
                    num_experts = int(input(f"How many expert types in {category_name}? "))
                    if num_experts > 0:
                        break
                    else:
                        print("Please enter a positive number")
                except ValueError:
                    print("Please enter a valid number")
            
            # Create each expert
            for j in range(num_experts):
                expert_name = input(f"  Name for expert {j+1} in {category_name}: ")
                
                # Show available models and let user select one
                print(f"\n  Select a model for {expert_name}:")
                for i, model_name in enumerate(self.available_models, 1):
                    if model_name == "gemma3":
                        print(f"  {i}. {model_name} (recommended)")
                    else:
                        print(f"  {i}. {model_name}")
                
                while True:
                    model_choice = input(f"  Enter model number (1-{len(self.available_models)}, default: gemma3): ")
                    
                    if model_choice == "":
                        model = "gemma3" if "gemma3" in self.available_models else self.available_models[0]
                        break
                    
                    try:
                        choice_idx = int(model_choice) - 1
                        if 0 <= choice_idx < len(self.available_models):
                            model = self.available_models[choice_idx]
                            break
                        else:
                            print(f"  Please enter a number between 1 and {len(self.available_models)}")
                    except ValueError:
                        print("  Please enter a valid number or press Enter for the default model")
                
                # Create a system prompt or use default
                use_default = input(f"  Use default system prompt for {expert_name}? (y/n): ").lower() == 'y'
                
                if use_default:
                    system_prompt = f"You are an expert in {expert_name}. Provide knowledgeable, accurate, and helpful responses about {expert_name}."
                else:
                    print(f"  Enter system prompt for {expert_name} (or press Enter for default):")
                    system_prompt = input("  > ") or f"You are an expert in {expert_name}. Provide knowledgeable, accurate, and helpful responses about {expert_name}."
                
                category.add_child(DecisionTreeNode(
                    expert_name,
                    is_leaf=True,
                    model=model,
                    system_prompt=system_prompt
                ))
        
        return root
    
    def save_tree(self, root, filename):
        """
        Save the decision tree to a JSON file
        """
        tree_data = root.to_dict()
        
        os.makedirs("decision_trees", exist_ok=True)
        filepath = os.path.join("decision_trees", filename)
        
        with open(filepath, 'w') as f:
            json.dump(tree_data, f, indent=2)
        
        print(f"\nDecision tree saved to {filepath}")
    
    def load_tree(self, filename):
        """
        Load a decision tree from a JSON file
        """
        filepath = os.path.join("decision_trees", filename)
        
        try:
            with open(filepath, 'r') as f:
                tree_data = json.load(f)
            
            return DecisionTreeNode.from_dict(tree_data)
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            return None
        except json.JSONDecodeError:
            print(f"Error: File {filepath} contains invalid JSON")
            return None
    
    def list_saved_trees(self):
        """
        List all saved decision trees
        """
        os.makedirs("decision_trees", exist_ok=True)
        files = [f for f in os.listdir("decision_trees") if f.endswith('.json')]
        
        if not files:
            print("\nNo saved decision trees found")
            return []
        
        print("\nSaved decision trees:")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
        
        return files
    
    def run_conversation(self):
        """
        Run the conversation with the selected expert
        """
        # Verify the model exists, if not select a different one
        if self.model not in self.available_models:
            print(f"\nWarning: Model '{self.model}' is not available.")
            self.model = select_model(default_model="gemma3")
        
        # Record initial setup in conversation history
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # Initialize the expert
        print(f"\nInitializing {self.expert_type} expert using {self.model} model...\n")
        
        # Ask one question before beginning the main conversation
        initial_question_prompt = f"{self.system_prompt}\n\nAsk the user one thoughtful question about {self.expert_type} to start the conversation. Make it engaging and specific to the field."
        initial_question = query_ollama(initial_question_prompt, self.model)
        
        print(f"Expert: {initial_question}")
        
        # Record this in the conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": initial_question
        })
        
        # Main conversation loop
        while True:
            # Get user input
            user_input = input("\nYou (type 'exit' to end): ")
            
            # Record user input in conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Check if user wants to exit
            if user_input.lower() == 'exit':
                print("\nThank you for using the Ollama Expert System. Goodbye!")
                break
            
            # Create the full prompt with conversation history
            full_prompt = self.system_prompt + "\n\n"
            
            # Include the last few exchanges to keep context but avoid token limits
            recent_history = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
            
            for entry in recent_history:
                if entry["role"] == "user":
                    full_prompt += f"User: {entry['content']}\n"
                elif entry["role"] == "assistant" and entry["role"] != "system":
                    full_prompt += f"Expert: {entry['content']}\n"
            
            full_prompt += "Expert: "
            
            # Get response from Ollama
            response = query_ollama(full_prompt, self.model)
            
            # Display the response
            print(f"\nExpert: {response}")
            
            # Record the response in conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
    
    def save_conversation_history(self):
        """
        Save the conversation history to a JSON file
        """
        # Create directory for history files if it doesn't exist
        os.makedirs("conversation_history", exist_ok=True)
        
        # Save the conversation history to a JSON file
        safe_expert_type = self.expert_type.replace(' ', '_').replace('/', '_')
        filename = f"conversation_history/{safe_expert_type}_history_{self.timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        
        print(f"\nConversation history saved to {filename}")
    
    def run(self):
        """
        Main method to run the expert system
        """
        # Welcome message
        print("\n" + "=" * 60)
        print("Welcome to the Ollama Custom Decision Tree Expert System!")
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
            print("\nNo models found. You need to pull models before using the expert system.")
            print("Example: ollama pull gemma3")
            print("Example: ollama pull llama2")
            sys.exit(1)
        
        # Main menu
        options = [
            "Use default decision tree",
            "Create a new decision tree",
            "Load a saved decision tree",
            "Exit"
        ]
        
        choice = self.display_menu(options, "Main Menu")
        
        if choice == 0:  # Use default
            self.root = self.create_default_tree()
        elif choice == 1:  # Create new
            self.root = self.create_custom_tree()
            
            # Ask if user wants to save the tree
            if input("\nDo you want to save this decision tree? (y/n): ").lower() == 'y':
                filename = input("Enter filename (without path, will be saved in decision_trees/): ")
                if not filename.endswith('.json'):
                    filename += '.json'
                self.save_tree(self.root, filename)
        elif choice == 2:  # Load saved
            files = self.list_saved_trees()
            if files:
                file_choice = self.display_menu(files, "Select a decision tree to load")
                self.root = self.load_tree(files[file_choice])
                if not self.root:
                    print("Failed to load decision tree. Exiting.")
                    return
            else:
                print("No saved trees available. Exiting.")
                return
        else:  # Exit
            print("Goodbye!")
            return
        
        # Navigate the tree to select an expert
        expert_node = self.navigate_tree(self.root)
        
        if expert_node:
            self.expert_type = expert_node.name
            self.model = expert_node.model
            self.system_prompt = expert_node.system_prompt
            
            # Run the conversation
            self.run_conversation()
            
            # Save the conversation history
            self.save_conversation_history()


if __name__ == "__main__":
    expert_system = OllamaExpertSystem()
    expert_system.run()
