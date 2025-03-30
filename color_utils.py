#!/usr/bin/env python3
"""
Color utilities for the Ollama Decision Tree Expert System
Provides consistent color formatting across all scripts
"""
import os
import sys
import platform
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

# Define standard colors
SYSTEM_COLOR = Fore.CYAN
USER_COLOR = Fore.GREEN
EXPERT_COLOR = Fore.YELLOW
OPTION_ID_COLOR = Fore.CYAN + Style.BRIGHT
OPTION_TEXT_COLOR = Fore.WHITE
ERROR_COLOR = Fore.RED
SUCCESS_COLOR = Fore.GREEN + Style.BRIGHT
HELP_COLOR = Fore.MAGENTA
HEADER_COLOR = Fore.CYAN + Style.BRIGHT
RESET = Style.RESET_ALL

# Flag to enable/disable colors
_colors_enabled = True

def disable_colors():
    """Disable all colors"""
    global _colors_enabled
    _colors_enabled = False

def enable_colors():
    """Enable all colors"""
    global _colors_enabled
    _colors_enabled = True

def is_colors_supported():
    """Check if the terminal supports colors"""
    # Check if colors are explicitly disabled
    if os.environ.get('NO_COLOR') is not None:
        return False
    
    # Check if output is redirected
    if not sys.stdout.isatty():
        return False
    
    # Check for known terminals that support colors
    plat = platform.system()
    if plat == 'Windows':
        return 'ANSICON' in os.environ or 'WT_SESSION' in os.environ or os.environ.get('TERM_PROGRAM') == 'vscode'
    else:
        return True

def colored(text, color):
    """Return colored text if colors are enabled"""
    if _colors_enabled and is_colors_supported():
        return f"{color}{text}{RESET}"
    return text

def print_system(text):
    """Print system message"""
    print(colored(text, SYSTEM_COLOR))

def print_header(text):
    """Print header"""
    print(colored(text, HEADER_COLOR))

def print_expert(text):
    """Print expert response"""
    print(f"{colored('Expert:', EXPERT_COLOR)} {text}")

def print_options(options):
    """Print options in a formatted way"""
    print(colored("\nOptions:", SYSTEM_COLOR))
    for option_id, option_text in options:
        print(f"{colored(f'{option_id})', OPTION_ID_COLOR)} {option_text}")

def print_error(text):
    """Print error message"""
    print(colored(f"Error: {text}", ERROR_COLOR))

def print_success(text):
    """Print success message"""
    print(colored(text, SUCCESS_COLOR))

def print_help(text):
    """Print help text"""
    print(colored(text, HELP_COLOR))

def colored_input(prompt, color=USER_COLOR):
    """Get input with colored prompt"""
    return input(colored(prompt, color))

def print_separator(char="=", length=60):
    """Print a separator line"""
    print(colored(char * length, SYSTEM_COLOR))

def print_welcome(title):
    """Print a welcome message with a title"""
    print_separator()
    print_header(title)
    print_separator()

def format_command(command):
    """Format a command for display"""
    return colored(command, HELP_COLOR)

# Auto-detect if colors should be enabled
if not is_colors_supported():
    disable_colors()
