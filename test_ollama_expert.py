import subprocess
import time
import os

def test_ollama_expert():
    # Start the ollama_expert.py process
    process = subprocess.Popen(
        ["python", "ollama_expert.py", "--expert", "test expert", "--no-color"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait for the model selection prompt
    time.sleep(2)
    
    # Select the default model (press Enter)
    process.stdin.write("\n")
    process.stdin.flush()
    
    # Wait for the initial question
    time.sleep(5)
    
    # Type "exit" to test the exit command
    process.stdin.write("exit\n")
    process.stdin.flush()
    
    # Wait for the save prompt
    time.sleep(1)
    
    # Type "n" to not save
    process.stdin.write("n\n")
    process.stdin.flush()
    
    # Wait for the process to complete
    time.sleep(2)
    
    # Check if any files were created
    files_before = set(os.listdir("conversation_history"))
    
    # Print the output
    stdout, stderr = process.communicate(timeout=5)
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    
    # Check if any new files were created
    files_after = set(os.listdir("conversation_history"))
    new_files = files_after - files_before
    
    print("New files created:", new_files)
    
    return process.returncode

if __name__ == "__main__":
    exit_code = test_ollama_expert()
    print(f"Exit code: {exit_code}")
