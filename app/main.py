import sys
import shutil


def main():
    builtins = ["echo", "exit", "type"]
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        
        # .strip() removes any accidental leading/trailing spaces or newlines
        user_input = input().strip()
        
        if not user_input:
            continue
        
        parts = user_input.split()
        cmd = parts[0]
        
        # Handle exit: check if the first word is 'exit'
        if cmd == "exit":
            # The challenge usually expects an exit code. 
            # If they type 'exit 0', we exit. If just 'exit', we also exit.
            sys.exit(0) 
            
        elif cmd == "echo":
            print(" ".join(parts[1:]))
            
        elif cmd == "type":
            if len(parts) > 1:
                target = parts[1]
                if target in builtins:
                    print(f"{target} is a shell builtin")
                elif path := shutil.which(target):
                    print(f"{target} is {path}")
                else:
                    print(f"{target}: not found")
            else:
                # Handle cases where user just types 'type' with no argument
                pass
                
        else:
            print(f"{user_input}: not found")
    


if __name__ == "__main__":
    main()
