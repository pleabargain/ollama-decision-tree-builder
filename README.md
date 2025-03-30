# repo
https://github.com/pleabargain/ollama-decision-tree-builder
# bOllama Decision Tree Expert System

This project provides a flexible system for creating and interacting with AI experts using Ollama. It allows users to select different types of experts through a decision tree interface and have conversations with them.

![Ollama Decision Tree Expert System](https://ollama.ai/public/ollama.png)

## Features

- Basic expert selection and conversation with `ollama_expert.py`
- Predefined decision tree navigation with `decision_tree_expert.py`
- Fully customizable decision trees with `custom_decision_tree.py`
- **NEW: JSON-based decision tree conversations** with `decision_tree_conversation.py`
- **NEW: Testing and validation** with `test_decision_tree.py`
- **NEW: Colorized interface** for improved readability and user experience
- **NEW: Error correction and response validation** for more reliable AI responses
- **NEW: Automated input simulation** with `fake-user-input.py`
- **NEW: Schema-compliant JSON output** for all conversation histories
- Conversation history saved as JSON files
- Support for different Ollama models based on expert type
- Save and exit functionality at any point in the conversation
- Multiple choice questions with free-text response options
- Extensive error tracking and logging
- Format conversion for different conversation history types

## Requirements

- Python 3.6+
- **Ollama running locally** (default: http://localhost:11434)
  - The application checks if Ollama is running and will exit if it's not
  - You must start Ollama before running any of the scripts
- At least one Ollama model pulled (recommended: gemma3, llama2, or codellama)
- Required Python packages:
  - requests
  - json (standard library)
  - datetime (standard library)
  - os (standard library)
  - sys (standard library)

## Installation

1. Make sure you have Ollama installed and running on your system
   - Visit [Ollama's website](https://ollama.ai/) for installation instructions
   - **Start the Ollama service** before running any scripts
   - Pull at least one model: `ollama pull gemma3` (or llama2, codellama, etc.)

2. Install the required Python packages:
   ```
   pip install requests
   ```

3. Clone or download this repository to your local machine

## Usage

### Quick Start

The easiest way to get started is to use the launcher script:

```
python run.py
```

This will present a menu where you can choose which system to run.

### Testing Your Ollama Connection

Before using the expert systems, you should verify that Ollama is properly installed and running:

```
python test_ollama_connection.py
```

This script will:
- Check if Ollama is running
- List available models
- Verify that recommended models are installed
- Test a simple query to ensure everything is working

If the test fails, make sure:
1. Ollama is installed and running
2. You have pulled at least one model (e.g., `ollama pull gemma3`)
3. Your firewall isn't blocking connections to localhost:11434

### Basic Expert System

Run the basic expert system directly with:

```
python ollama_expert.py
```

This script:
- Prompts you to specify what type of expert you want to talk to
- Initializes the expert using Ollama
- Asks one initial question to start the conversation (now as a multiple choice question)
- Presents multiple choice options when appropriate
- Allows you to select options by letter/number or type your own response
- Supports commands like 'save', 'exit', and 'help'
- Records all interactions in a JSON file

Available commands during conversation:
- `help` - Show available commands
- `save` - Save the current conversation
- `exit` - Save and exit the conversation

### Decision Tree Expert System

Run the predefined decision tree expert system with:

```
python decision_tree_expert.py
```

This script:
- Presents a menu of expert categories (Technology, Science, Business, etc.)
- Allows you to select a specific expert within the chosen category
- Initializes the expert using an appropriate Ollama model
- Asks one initial question to start the conversation
- Records all interactions in a JSON file that complies with the decision tree schema

You can also run it with an input file to automate the conversation:

```
python decision_tree_expert.py fake-user-input.json
```

When run with an input file, the script:
- Reads predefined inputs from the JSON file (model, category, expert type, conversation)
- Runs through the conversation automatically
- Saves the output as a valid JSON file according to the schema

### Custom Decision Tree Expert System

Run the fully customizable decision tree expert system with:

```
python custom_decision_tree.py
```

This script offers three main options:

1. **Use default decision tree** - Similar to the predefined decision tree
2. **Create a new decision tree** - Guide you through creating your own custom decision tree
   - Define your own categories and expert types
   - Specify which Ollama model to use for each expert
   - Create custom system prompts or use defaults
   - Save your custom tree for future use
3. **Load a saved decision tree** - Use a previously saved custom decision tree

### JSON-based Decision Tree Conversation System

Run the new JSON-based decision tree conversation system with:

```
python decision_tree_conversation.py
```

This advanced system offers:

1. **Structured conversations** - Based on a JSON decision tree template
2. **Multiple choice questions** - With the ability to select options by number
3. **Free-text responses** - Users can type their own responses instead of selecting options
4. **Save and exit at any time** - Use commands like `save`, `exit`, `help`, and `back`
5. **Comprehensive conversation history** - All interactions are saved in a structured JSON format
6. **Expert-specific fields** - The JSON includes dedicated fields for expert type and questions
7. **Load and continue conversations** - Resume previous conversations from where you left off
8. **Choose from multiple templates** - Start with different conversation templates

When you run the script, you'll be presented with options to:
1. Start a new conversation with a template
2. Continue an existing conversation

Available commands during conversation:
- `help` - Show available commands
- `save` - Save the current conversation
- `exit` - Save and exit the conversation
- `back` - Go back to the previous question

You can also specify a template or conversation file directly:
```
python decision_tree_conversation.py path/to/your/file.json
```

### Testing and Validation

Run the test script to validate your templates and conversation history files:

```
python test_decision_tree.py
```

This script offers:

1. **Template validation** - Checks all templates in the templates directory
2. **Conversation history validation** - Validates all conversation history files
3. **Node navigation testing** - Tests navigation between nodes in the decision tree
4. **Format conversion** - Tests conversion between different conversation history formats
5. **Detailed error reporting** - Provides comprehensive error messages and logs

You can also run specific tests using command-line arguments:

```
python test_decision_tree.py --templates  # Test only templates
python test_decision_tree.py --histories  # Test only conversation histories
python test_decision_tree.py --navigation  # Test only node navigation
python test_decision_tree.py --conversion  # Test only format conversion
```

The validation process checks for:
- Required fields in the metadata section
- Proper structure of the conversation_flow array
- Valid node definitions with required fields
- Proper references between nodes
- Correct format of conversation_history entries

When validation fails, the script provides detailed error messages indicating which fields are missing or incorrectly formatted, making it easy to identify and fix issues.

### Schema Validation

The system now ensures that all conversation history files comply with the JSON schema defined in `templates/decision_tree_schema.json`. This schema defines the required structure for decision tree conversations, including:

1. **Metadata section** - Contains information about the decision tree, such as title, version, expert type, etc.
2. **Conversation_flow array** - Defines the nodes, questions, options, and navigation paths
3. **Conversation_history array** - Records the actual conversation, including timestamps, user responses, and assistant responses

You can validate existing conversation history files against the schema using:

```
python test_decision_tree.py --histories
```

To validate a specific file:

```
python fake-user-input.py
```

This will:
1. Create a sample conversation
2. Generate a schema-compliant JSON file
3. Validate both new and existing files in the conversation_history directory

#### Converting Old Format to Schema-Compliant Format

If you have conversation history files in the old format (a simple array of messages), you can convert them to the new schema-compliant format using:

```
python decision_tree_conversation.py
```

Then select "Continue an existing conversation" and choose the file you want to convert. The system will automatically:
1. Detect the old format
2. Convert it to the new schema-compliant format
3. Save it as a new file with the proper structure

#### Example of Valid Schema-Compliant File

The `Fitness_history_20250330_123837.json` and `Cybersecurity_history_20250330_120941.json` files are examples of valid schema-compliant files. They include:

- A complete metadata section
- A properly structured conversation_flow array
- A detailed conversation_history array with all required fields

These files were generated using the updated `decision_tree_expert.py` script, which now automatically formats all output according to the schema.

## Conversation History

All conversations are saved in JSON files in the `conversation_history` directory with the naming format:

For basic and traditional decision tree conversations:
```
{expert_type}_history_{timestamp}.json
```

For JSON-based decision tree conversations:
```
{expert_type}_decision_tree_{timestamp}.json
```

The JSON-based decision tree conversations include:
- The complete decision tree structure
- All questions asked
- Options presented to the user
- User's responses (both multiple choice and free text)
- The path taken through the decision tree

## Decision Trees

### Custom Decision Trees
Custom decision trees for the traditional system are saved in the `decision_trees` directory as JSON files. You can:
- Create new trees through the interactive interface
- Edit the JSON files directly if you need more advanced customization
- Share tree definitions with others

### Decision Tree Templates and Schema

The system now includes:

1. **Generic Schema** (`decision_tree_schema.json`) - A blank template with documentation that serves as a starting point for creating new decision trees
2. **IT Career Template** (`IT_career_decision_tree_20250330.json`) - A specific implementation focused on IT career counseling
3. **Templates Directory** - All templates are stored in the `templates/` directory

The schema includes:
- Documentation on required fields and their purpose
- Examples of different node types
- Best practices for creating effective decision trees
- A minimal structure that can be extended for any domain

You can create custom templates by:
1. Starting with the generic schema and adding your own nodes
2. Copying and modifying an existing template
3. Exporting a conversation history and modifying it

Templates should be placed in the `templates/` directory to be automatically detected by the system.

## Examples

### Basic Expert Interaction

```
Welcome to the Ollama Expert System!
What type of expert would you like to talk to today? Python Programming

Initializing Python Programming expert...

Expert: What's your experience level with Python, and what specific areas or libraries are you most interested in learning more about?

You (type 'exit' to end): I'm intermediate and interested in machine learning

Expert: That's great! Python is an excellent language for machine learning due to its readability, extensive libraries, and strong community support.

For machine learning in Python, here are some key libraries and frameworks you might want to explore:

1. **NumPy and Pandas**: These form the foundation for data manipulation and numerical computing in Python.

2. **Scikit-learn**: A user-friendly library for classical machine learning algorithms (classification, regression, clustering, etc.) with consistent APIs.

3. **TensorFlow and PyTorch**: The two most popular deep learning frameworks. PyTorch is often favored for research due to its dynamic computation graph, while TensorFlow (with Keras) is widely used in production.

4. **Matplotlib and Seaborn**: Essential for data visualization and understanding your datasets.

As an intermediate Python programmer interested in machine learning, you might want to:

- Strengthen your understanding of NumPy, Pandas, and data preprocessing techniques
- Work through some end-to-end ML projects using Scikit-learn
- Gradually move to deep learning with either PyTorch or TensorFlow

Is there a specific area within machine learning you're most interested in, such as computer vision, natural language processing, or reinforcement learning?

You (type 'exit' to end): exit
Thank you for using the Ollama Expert System. Goodbye!

Conversation history saved to Python_Programming_history_20250330_085700.json
```

### Custom Decision Tree Creation

```
Welcome to the Ollama Custom Decision Tree Expert System!
============================================================

Main Menu
=========
1. Use default decision tree
2. Create a new decision tree
3. Load a saved decision tree
4. Exit

Enter your choice (number): 2

Creating a custom decision tree
===============================

How many main categories do you want? 2

Name for category 1: Programming
How many expert types in Programming? 2
  Name for expert 1 in Programming: Python
  Model to use for Python (default: llama2): codellama
  Use default system prompt for Python? (y/n): y
  Name for expert 2 in Programming: JavaScript
  Model to use for JavaScript (default: llama2): codellama
  Use default system prompt for JavaScript? (y/n): n
  Enter system prompt for JavaScript (or press Enter for default):
  > You are a JavaScript expert. Provide detailed code examples and best practices for modern JavaScript development including ES6+ features, frameworks like React, and Node.js.

Name for category 2: Science
How many expert types in Science? 1
  Name for expert 1 in Science: Physics
  Model to use for Physics (default: llama2): 
  Use default system prompt for Physics? (y/n): y

Do you want to save this decision tree? (y/n): y
Enter filename (without path, will be saved in decision_trees/): my_custom_tree.json

Decision tree saved to decision_trees/my_custom_tree.json

Select a Root
============
1. Programming
2. Science

Enter your choice (number): 1

Select a Programming
===================
1. Python
2. JavaScript

Enter your choice (number): 2

Initializing JavaScript expert using codellama model...

Expert: What's your experience with JavaScript frameworks like React, Angular, or Vue, and which one are you currently working with or interested in learning more about?
```

## Extending the System

You can extend this system by:
- Adding more expert types and categories
- Integrating with different Ollama models
- Customizing system prompts for more specialized experts
- Modifying the conversation flow or adding more features

### Automated Input Simulation

You can simulate user input for the decision_tree_expert.py script using:

```
python fake-user-input.py
```

This script:
- Creates a JSON file with predefined inputs (model, category, expert type, conversation)
- Runs decision_tree_expert.py with this input file
- Verifies that the output matches the schema in templates/decision_tree_schema.json
- Reports on the validity of the generated JSON files

This is particularly useful for:
- Testing the system with different inputs
- Generating example conversations
- Ensuring that all output files comply with the schema
- Automating the creation of decision tree conversations

## Model Selection

The updated system now provides model selection capabilities:

- All scripts check if Ollama is running before starting
- Available models are detected automatically
- Users can select which model to use from a numbered list
- The default model is now `llama3.2` (falls back to the first available model)
- The system always respects the user's model selection as the primary choice
- Custom decision trees allow selecting different models for each expert type

## Colorized Interface

The system now features a colorized interface for improved readability and user experience:

- **System messages** are displayed in cyan
- **Expert responses** are highlighted in yellow
- **User prompts** appear in green
- **Options and menus** use bright cyan for identifiers
- **Error messages** are shown in red
- **Success messages** appear in bright green
- **Help text and commands** are displayed in magenta

You can disable colors using the `--no-color` command-line option:

```
python run.py --no-color
python ollama_expert.py --no-color
```

Colors are also automatically disabled in environments that don't support them, such as when output is redirected to a file.

## Error Correction and Response Validation

The system now includes automatic error correction and response validation to ensure high-quality AI responses:

- **Response Validation**: All responses from Ollama are validated before being shown to the user
- **Error Detection**: The system can detect common error patterns, incomplete responses, and invalid outputs
- **Automatic Retries**: If an invalid response is detected, the system will automatically retry the query
- **Response Sanitization**: All responses are sanitized to remove any potential control characters or invalid Unicode
- **Graceful Degradation**: If multiple retries fail, the system will provide a helpful fallback response

This functionality helps ensure that:
1. Users don't see error messages or incomplete responses
2. The conversation flows naturally even if there are temporary issues with the AI model
3. The system remains robust against various types of model failures
4. All responses are properly formatted and safe to display

The error correction system is configurable with a maximum number of retries and can be extended with additional validation rules as needed.

## Command-Line Options

The scripts now support various command-line options:

### run.py
```
python run.py --no-color     # Disable colored output
```

### ollama_expert.py
```
python ollama_expert.py --no-color     # Disable colored output
python ollama_expert.py --expert "Python Programming"  # Specify expert type directly
```

### decision_tree_expert.py
```
python decision_tree_expert.py input-file.json  # Run with predefined inputs from a JSON file
```

### fake-user-input.py
```
python fake-user-input.py  # Create input file and run decision_tree_expert.py with it
```

## File Descriptions

This section provides detailed descriptions of each Python file in the project and what they do:

### Core Files

- **run.py** - The main launcher script that presents a menu to choose which system to run.
- **ollama_expert.py** - Implements the basic expert system that allows users to specify an expert type and have a conversation.
- **ollama_utils.py** - Contains utility functions for interacting with the Ollama API, including sending prompts and receiving responses.
- **color_utils.py** - Provides functions for colorizing terminal output to improve readability and user experience.
- **validate_output.py** - Implements validation and error correction for AI responses to ensure high-quality interactions.

### Decision Tree Implementation

- **decision_tree_expert.py** - Implements the predefined decision tree expert system with categories and expert types.
- **custom_decision_tree.py** - Provides a fully customizable decision tree system that allows users to create, save, and load custom trees.
- **decision_tree_conversation.py** - Implements the JSON-based decision tree conversation system with structured conversations.

### Test and Validation Files

- **test_decision_tree.py** - Tests and validates templates and conversation history files against the schema.
- **test_ollama_connection.py** - Verifies that Ollama is properly installed, running, and has the required models.
- **test_ollama_expert.py** - Tests the basic expert system functionality.
- **test_exit_command.py** - Tests the exit command functionality across different scripts.
- **test_save_function.py** - Tests the save functionality to ensure conversation histories are properly saved.
- **fake-user-input.py** - Creates sample conversations and tests the system with automated input simulation.

## Test Scripts and Their Usage

The project includes several test scripts to ensure everything is working correctly:

### test_ollama_connection.py

This script verifies your Ollama installation and connection:

```
python test_ollama_connection.py
```

- Checks if Ollama is running on the default port (11434)
- Lists all available models
- Verifies that recommended models are installed
- Tests a simple query to ensure the API is responding correctly
- Provides detailed error messages if any issues are found

### test_decision_tree.py

This comprehensive test script validates templates and conversation histories:

```
python test_decision_tree.py
```

Options:
- `--templates` - Test only templates
- `--histories` - Test only conversation histories
- `--navigation` - Test only node navigation
- `--conversion` - Test only format conversion

The script checks:
- Schema compliance for all JSON files
- Required fields in metadata sections
- Proper structure of conversation flows
- Valid node definitions and references
- Correct format of conversation histories

All test results are logged to `test_decision_tree.log` for review.

### test_exit_command.py

Tests the exit command functionality:

```
python test_exit_command.py
```

- Verifies that the exit command works correctly in all scripts
- Ensures that conversations are properly saved before exiting
- Checks that the program terminates gracefully

### test_save_function.py

Tests the save functionality:

```
python test_save_function.py
```

- Verifies that conversations are saved correctly
- Ensures that saved files comply with the schema
- Checks that all required fields are included in the saved files

### test_ollama_expert.py

Tests the basic expert system:

```
python test_ollama_expert.py
```

- Verifies that the expert system initializes correctly
- Tests conversation flow with predefined inputs
- Ensures that responses are properly validated

### fake-user-input.py

Creates and tests automated conversations:

```
python fake-user-input.py
```

- Generates a sample conversation with predefined inputs
- Creates a schema-compliant JSON file
- Runs decision_tree_expert.py with the generated input
- Validates the output against the schema
- Useful for testing and generating example conversations

## Troubleshooting

- **Ollama Must Be Running**: The most common error is trying to use the system without Ollama running. Make sure to start Ollama first.
- **No Models Available**: If you see "No models found", you need to pull at least one model with `ollama pull modelname`
- **Model Not Found**: If a specific model isn't working, ensure you've pulled it with `ollama pull modelname`
- **Connection Errors**: Check if your firewall is blocking connections to localhost:11434
- **Color Issues**: If colors appear incorrectly in your terminal, use the `--no-color` option
- **Duplicated Output**: If you see duplicated output in the menu, try clearing your terminal before running the script
- For any other issues, check the error messages for guidance
