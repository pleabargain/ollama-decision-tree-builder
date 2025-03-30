import json
import os
import sys
import jsonschema

def validate_against_schema(output_file, schema_file):
    """
    Validate a JSON file against a JSON schema
    """
    # Load the output file
    with open(output_file, 'r') as f:
        output_data = json.load(f)
    
    # Load the schema file
    with open(schema_file, 'r') as f:
        schema_data = json.load(f)
    
    # Validate the output against the schema
    try:
        jsonschema.validate(instance=output_data, schema=schema_data)
        print(f"SUCCESS: {output_file} is valid against the schema")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"ERROR: {output_file} is not valid against the schema")
        print(f"Validation error: {e}")
        return False

def main():
    # Check if jsonschema is installed
    try:
        import jsonschema
    except ImportError:
        print("Installing jsonschema...")
        os.system(f"{sys.executable} -m pip install jsonschema")
        import jsonschema
    
    # Find the most recent output file
    conversation_dir = "conversation_history"
    if not os.path.exists(conversation_dir):
        print(f"ERROR: {conversation_dir} directory does not exist")
        return False
    
    files = [f for f in os.listdir(conversation_dir) if f.endswith('.json') and not f.endswith('_raw_history_.json')]
    if not files:
        print(f"ERROR: No JSON files found in {conversation_dir}")
        return False
    
    # Sort files by modification time (newest first)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(conversation_dir, x)), reverse=True)
    latest_file = os.path.join(conversation_dir, files[0])
    
    print(f"Latest output file: {latest_file}")
    
    # Validate against the schema
    schema_file = "templates/decision_tree_schema.json"
    if not os.path.exists(schema_file):
        print(f"ERROR: Schema file {schema_file} does not exist")
        return False
    
    return validate_against_schema(latest_file, schema_file)

if __name__ == "__main__":
    success = main()
    if success:
        print("\nValidation successful! The output matches the schema.")
    else:
        print("\nValidation failed! The output does not match the schema.")
