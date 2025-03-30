#!/usr/bin/env python3
"""
Test script for the Decision Tree Conversation System

This script tests the functionality of the decision_tree_conversation.py script,
including JSON validation, node navigation, and conversation history loading.
"""
import os
import sys
import json
import logging
import argparse
from decision_tree_conversation import DecisionTreeConversation

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_decision_tree.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_decision_tree")

def test_json_validation(directory, extension=".json"):
    """
    Test JSON validation for all files in the directory
    """
    print(f"\nTesting JSON validation for files in {directory}...")
    
    # Get all JSON files in the directory
    files = [f for f in os.listdir(directory) if f.endswith(extension)]
    
    if not files:
        print(f"No {extension} files found in {directory}")
        return []
    
    results = []
    
    # Create a conversation object for testing
    conversation = DecisionTreeConversation(test_mode=True)
    
    # Test each file
    for file in files:
        file_path = os.path.join(directory, file)
        print(f"Testing {file}...")
        
        try:
            # Load the file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Try to convert the format if needed
            data = conversation.convert_conversation_format(data)
            
            # Validate the structure
            valid, message = conversation.validate_json_structure(data)
            
            if valid:
                print(f"  ✓ {file} is valid or can be converted")
                results.append((file, "PASS"))
            else:
                print(f"  ✗ {file} is invalid: {message}")
                results.append((file, "FAIL", message))
        except Exception as e:
            print(f"  ✗ Error validating {file}: {e}")
            results.append((file, "ERROR", str(e)))
    
    return results

def test_node_navigation(template_file):
    """
    Test node navigation using a template file
    """
    print(f"\nTesting node navigation using {template_file}...")
    
    results = []
    
    try:
        # Create a conversation object for testing
        conversation = DecisionTreeConversation(template_path=template_file, test_mode=True)
        
        # Load the template
        if conversation.load_decision_tree(is_template=True):
            # Get the root node
            root_node = conversation.get_current_node()
            
            if root_node:
                print(f"  ✓ Root node found: {root_node['node_id']}")
                results.append(("Root node", "PASS"))
                
                # Test navigation to another node
                if root_node["question_type"] == "multiple_choice" and "options" in root_node:
                    option = root_node["options"][0]
                    next_node_id = option["next_node"]
                    
                    # Simulate selecting this option
                    conversation.process_response(option["option_id"], root_node)
                    
                    # Check if we navigated to the correct node
                    if conversation.current_node_id == next_node_id:
                        print(f"  ✓ Navigation to {next_node_id} successful")
                        results.append(("Option selection", "PASS"))
                    else:
                        print(f"  ✗ Navigation failed: expected {next_node_id}, got {conversation.current_node_id}")
                        results.append(("Option selection", "FAIL", f"Expected {next_node_id}, got {conversation.current_node_id}"))
                else:
                    print("  ✗ Root node is not a multiple choice node or has no options")
                    results.append(("Option selection", "SKIP", "Root node is not a multiple choice node or has no options"))
            else:
                print("  ✗ Root node not found")
                results.append(("Root node", "FAIL", "Root node not found"))
        else:
            print("  ✗ Failed to load template")
            results.append(("Template loading", "FAIL", "Failed to load template"))
    except Exception as e:
        print(f"  ✗ Error testing node navigation: {e}")
        results.append(("Node navigation", "ERROR", str(e)))
    
    return results

def test_conversation_history_loading(history_file):
    """
    Test loading a conversation history file
    """
    print(f"\nTesting conversation history loading using {history_file}...")
    
    results = []
    
    try:
        # Create a conversation object for testing
        conversation = DecisionTreeConversation(template_path=history_file, test_mode=True)
        
        # Load the conversation history
        if conversation.load_decision_tree(is_template=False):
            print(f"  ✓ Conversation history loaded successfully")
            results.append(("History loading", "PASS"))
            
            # Check if the conversation history is not empty
            if conversation.conversation_history:
                print(f"  ✓ Conversation history has {len(conversation.conversation_history)} entries")
                results.append(("History entries", "PASS"))
                
                # Check if the current node is set correctly
                current_node = conversation.get_current_node()
                if current_node:
                    print(f"  ✓ Current node set to {conversation.current_node_id}")
                    results.append(("Current node", "PASS"))
                else:
                    print(f"  ✗ Current node {conversation.current_node_id} not found")
                    results.append(("Current node", "FAIL", f"Node {conversation.current_node_id} not found"))
            else:
                print("  ✗ Conversation history is empty")
                results.append(("History entries", "FAIL", "Conversation history is empty"))
        else:
            print("  ✗ Failed to load conversation history")
            results.append(("History loading", "FAIL", "Failed to load conversation history"))
    except Exception as e:
        print(f"  ✗ Error testing conversation history loading: {e}")
        results.append(("History loading", "ERROR", str(e)))
    
    return results

def test_format_conversion(history_file):
    """
    Test converting a conversation history file from the old format
    """
    print(f"\nTesting format conversion using {history_file}...")
    
    results = []
    
    try:
        # Load the file
        with open(history_file, 'r') as f:
            data = json.load(f)
        
        # Check if the file is in the old format
        if isinstance(data, list):
            print(f"  ✓ File is in the old format")
            results.append(("Old format", "PASS"))
            
            # Create a conversation object for testing
            conversation = DecisionTreeConversation(test_mode=True)
            
            # Convert the format
            converted_data = conversation.convert_conversation_format(data)
            
            # Check if the conversion was successful
            if isinstance(converted_data, dict) and "metadata" in converted_data and "conversation_flow" in converted_data:
                print(f"  ✓ Conversion successful")
                results.append(("Conversion", "PASS"))
                
                # Check if the expert type was extracted
                if converted_data["metadata"]["expert_type"] != "unknown":
                    print(f"  ✓ Expert type extracted: {converted_data['metadata']['expert_type']}")
                    results.append(("Expert type", "PASS"))
                else:
                    print("  ✗ Expert type not extracted")
                    results.append(("Expert type", "FAIL", "Expert type not extracted"))
                
                # Check if the conversation history was converted
                if converted_data["conversation_history"]:
                    print(f"  ✓ Conversation history converted with {len(converted_data['conversation_history'])} entries")
                    results.append(("History conversion", "PASS"))
                else:
                    print("  ✗ Conversation history not converted")
                    results.append(("History conversion", "FAIL", "Conversation history not converted"))
            else:
                print("  ✗ Conversion failed")
                results.append(("Conversion", "FAIL", "Conversion failed"))
        else:
            print(f"  ✗ File is not in the old format")
            results.append(("Old format", "SKIP", "File is not in the old format"))
    except Exception as e:
        print(f"  ✗ Error testing format conversion: {e}")
        results.append(("Format conversion", "ERROR", str(e)))
    
    return results

def run_all_tests():
    """
    Run all tests
    """
    all_results = []
    
    # Test JSON validation for templates
    templates_dir = "templates"
    if os.path.exists(templates_dir):
        template_results = test_json_validation(templates_dir)
        all_results.extend([("Template validation: " + r[0], r[1]) if len(r) == 2 else ("Template validation: " + r[0], r[1], r[2]) for r in template_results])
        
        # Test node navigation using the first template
        template_files = [f for f in os.listdir(templates_dir) if f.endswith(".json")]
        if template_files:
            template_file = os.path.join(templates_dir, template_files[0])
            navigation_results = test_node_navigation(template_file)
            all_results.extend([("Node navigation: " + r[0], r[1]) if len(r) == 2 else ("Node navigation: " + r[0], r[1], r[2]) for r in navigation_results])
    
    # Test JSON validation for conversation histories
    history_dir = "conversation_history"
    if os.path.exists(history_dir):
        history_results = test_json_validation(history_dir)
        all_results.extend([("History validation: " + r[0], r[1]) if len(r) == 2 else ("History validation: " + r[0], r[1], r[2]) for r in history_results])
        
        # Test conversation history loading using the first history file
        history_files = [f for f in os.listdir(history_dir) if f.endswith(".json")]
        if history_files:
            history_file = os.path.join(history_dir, history_files[0])
            loading_results = test_conversation_history_loading(history_file)
            all_results.extend([("History loading: " + r[0], r[1]) if len(r) == 2 else ("History loading: " + r[0], r[1], r[2]) for r in loading_results])
            
            # Test format conversion
            conversion_results = test_format_conversion(history_file)
            all_results.extend([("Format conversion: " + r[0], r[1]) if len(r) == 2 else ("Format conversion: " + r[0], r[1], r[2]) for r in conversion_results])
    
    # Print test summary
    print("\nTest Summary:")
    print("=" * 60)
    passed = sum(1 for result in all_results if result[1] == "PASS")
    failed = sum(1 for result in all_results if result[1] == "FAIL")
    errors = sum(1 for result in all_results if result[1] == "ERROR")
    skipped = sum(1 for result in all_results if result[1] == "SKIP")
    
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    print(f"Total: {len(all_results)}")
    
    if failed == 0 and errors == 0:
        print("\nAll tests passed!")
        return True
    else:
        print("\nSome tests failed or had errors. See log for details.")
        
        # Log detailed results
        logger.info("Test results:")
        for result in all_results:
            if result[1] == "PASS":
                logger.info(f"PASS: {result[0]}")
            elif result[1] == "FAIL":
                logger.error(f"FAIL: {result[0]} - {result[2]}")
            elif result[1] == "ERROR":
                logger.error(f"ERROR: {result[0]} - {result[2]}")
            elif result[1] == "SKIP":
                logger.warning(f"SKIP: {result[0]} - {result[2]}")
        
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Decision Tree Conversation System")
    parser.add_argument("--templates", action="store_true", help="Test template files")
    parser.add_argument("--histories", action="store_true", help="Test conversation history files")
    parser.add_argument("--navigation", action="store_true", help="Test node navigation")
    parser.add_argument("--loading", action="store_true", help="Test conversation history loading")
    parser.add_argument("--conversion", action="store_true", help="Test format conversion")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # If no arguments are provided, run all tests
    if not any(vars(args).values()):
        args.all = True
    
    if args.all:
        run_all_tests()
    else:
        all_results = []
        
        if args.templates:
            templates_dir = "templates"
            if os.path.exists(templates_dir):
                template_results = test_json_validation(templates_dir)
                all_results.extend([("Template validation: " + r[0], r[1]) if len(r) == 2 else ("Template validation: " + r[0], r[1], r[2]) for r in template_results])
        
        if args.navigation:
            templates_dir = "templates"
            if os.path.exists(templates_dir):
                template_files = [f for f in os.listdir(templates_dir) if f.endswith(".json")]
                if template_files:
                    template_file = os.path.join(templates_dir, template_files[0])
                    navigation_results = test_node_navigation(template_file)
                    all_results.extend([("Node navigation: " + r[0], r[1]) if len(r) == 2 else ("Node navigation: " + r[0], r[1], r[2]) for r in navigation_results])
        
        if args.histories:
            history_dir = "conversation_history"
            if os.path.exists(history_dir):
                history_results = test_json_validation(history_dir)
                all_results.extend([("History validation: " + r[0], r[1]) if len(r) == 2 else ("History validation: " + r[0], r[1], r[2]) for r in history_results])
        
        if args.loading:
            history_dir = "conversation_history"
            if os.path.exists(history_dir):
                history_files = [f for f in os.listdir(history_dir) if f.endswith(".json")]
                if history_files:
                    history_file = os.path.join(history_dir, history_files[0])
                    loading_results = test_conversation_history_loading(history_file)
                    all_results.extend([("History loading: " + r[0], r[1]) if len(r) == 2 else ("History loading: " + r[0], r[1], r[2]) for r in loading_results])
        
        if args.conversion:
            history_dir = "conversation_history"
            if os.path.exists(history_dir):
                history_files = [f for f in os.listdir(history_dir) if f.endswith(".json")]
                if history_files:
                    history_file = os.path.join(history_dir, history_files[0])
                    conversion_results = test_format_conversion(history_file)
                    all_results.extend([("Format conversion: " + r[0], r[1]) if len(r) == 2 else ("Format conversion: " + r[0], r[1], r[2]) for r in conversion_results])
        
        # Print test summary
        print("\nTest Summary:")
        print("=" * 60)
        passed = sum(1 for result in all_results if result[1] == "PASS")
        failed = sum(1 for result in all_results if result[1] == "FAIL")
        errors = sum(1 for result in all_results if result[1] == "ERROR")
        skipped = sum(1 for result in all_results if result[1] == "SKIP")
        
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print(f"Skipped: {skipped}")
        print(f"Total: {len(all_results)}")
