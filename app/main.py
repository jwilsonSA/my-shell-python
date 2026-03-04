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
        
        if cmd == "exit 0": # Handle exit
            break
            
        elif cmd == "echo":
            # Join all parts after the first one with a space
            print(" ".join(parts[1:]))
            
        elif cmd == "type":
            target = parts[1] if len(parts) > 1 else ""
            if target in builtins:
                print(f"{target} is a shell builtin")
            else:
                print(f"{target}: not found")
                
        else:
            print(f"{command}: not found")
    


if __name__ == "__main__":
    main()
