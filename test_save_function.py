import json
import os
from ollama_expert import save_conversation_as_decision_tree

def test_save_function():
    # Create a test conversation history
    conversation_history = [
        {
            "role": "system",
            "content": "You are an expert in test expert. Provide knowledgeable and helpful responses about test expert."
        },
        {
            "role": "assistant",
            "content": "Hello! I'm your test expert. What would you like to know?\n\na) Option 1\nb) Option 2\nc) Option 3"
        },
        {
            "role": "user",
            "content": "a"
        },
        {
            "role": "assistant",
            "content": "You selected Option 1. Here's more information about it."
        },
        {
            "role": "user",
            "content": "Tell me more"
        },
        {
            "role": "assistant",
            "content": "Here's more information about Option 1.\n\na) Sub-option 1\nb) Sub-option 2"
        }
    ]
    
    # Save the conversation as a decision tree
    expert_type = "test expert"
    timestamp = "20250330_test"
    filename = save_conversation_as_decision_tree(conversation_history, expert_type, timestamp)
    
    print(f"Saved to: {filename}")
    
    # Load the saved file and verify it matches the schema
    with open(filename, 'r') as f:
        decision_tree = json.load(f)
    
    # Check if the required fields are present
    required_fields = ["metadata", "conversation_flow", "conversation_history"]
    for field in required_fields:
        if field not in decision_tree:
            print(f"ERROR: Missing required field: {field}")
            return False
    
    # Check if metadata has required fields
    metadata_fields = ["title", "version", "created_at", "expert_type", "description", "author"]
    for field in metadata_fields:
        if field not in decision_tree["metadata"]:
            print(f"ERROR: Missing metadata field: {field}")
            return False
    
    # Check if conversation_flow has at least one node
    if len(decision_tree["conversation_flow"]) < 1:
        print("ERROR: conversation_flow should have at least one node")
        return False
    
    # Check if the first node has node_id "root"
    if decision_tree["conversation_flow"][0]["node_id"] != "root":
        print("ERROR: First node should have node_id 'root'")
        return False
    
    # Check if conversation_history entries have required fields
    if len(decision_tree["conversation_history"]) > 0:
        history_fields = ["timestamp", "node_id", "question", "user_response", "assistant_response"]
        for field in history_fields:
            if field not in decision_tree["conversation_history"][0]:
                print(f"ERROR: Missing conversation_history field: {field}")
                return False
    
    print("SUCCESS: Output matches the JSON schema")
    return True

if __name__ == "__main__":
    test_save_function()
