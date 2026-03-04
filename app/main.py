import sys


def main():
    # List of built-in commands for our shell
    builtins = ["echo", "exit", "type"]
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush() # Ensures the prompt appears immediately
        
        # Wait for user input
        command = input()
        
        if command == "exit 0":
            break
        
        
        # Split input into the command and its arguments
        parts = command.split()
        if not parts:
            continue
        
        cmd = parts[0]
        
        if cmd == "type":
            # Extract what they are trying to chec, e.g., 'type echo'
            target = parts[1] if len(parts) > 1 else ""
            if target in builtins:
                print(f"{target} is a shell builtin")
            else:
                print(f"{target} not found")
        elif cmd in builtins:
            print(f"{cmd} is a shell builtin")
        else:
            print(f"{command} is not found")
    


if __name__ == "__main__":
    main()
