# repo
https://github.com/pleabargain/ollama-decision-tree-builder

# Ollama Decision Tree Expert System

This project provides a flexible system for creating and interacting with AI experts using Ollama. It allows users to select different types of experts through a decision tree interface and have conversations with them.

![Ollama Decision Tree Expert System](https://ollama.ai/public/ollama.png)

## Features

- Basic expert selection and conversation with `ollama_expert.py`
- Predefined decision tree navigation with `decision_tree_expert.py`
- Fully customizable decision trees with `custom_decision_tree.py`
- **NEW: JSON-based decision tree conversations** with `decision_tree_conversation.py`
- **NEW: Testing and validation** with `test_decision_tree.py`
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
- Records all interactions in a JSON file

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

## Model Selection

The updated system now provides model selection capabilities:

- All scripts check if Ollama is running before starting
- Available models are detected automatically
- Users can select which model to use from a numbered list
- The default model is now `gemma3` (falls back to the first available model)
- For the decision tree and custom decision tree systems, model recommendations are made based on expert type
- Custom decision trees allow selecting different models for each expert type

## Troubleshooting

- **Ollama Must Be Running**: The most common error is trying to use the system without Ollama running. Make sure to start Ollama first.
- **No Models Available**: If you see "No models found", you need to pull at least one model with `ollama pull modelname`
- **Model Not Found**: If a specific model isn't working, ensure you've pulled it with `ollama pull modelname`
- **Connection Errors**: Check if your firewall is blocking connections to localhost:11434
- For any other issues, check the error messages for guidance
