import os
import sys, shutil, shlex, subprocess


def main():
    builtins = ["echo", "exit", "type", "pwd", "cd"]
        
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        
        user_input = input().strip()
        
        if not user_input:
            continue
        
        parts = shlex.split(user_input)
        cmd = parts[0]
        
        if cmd == "exit":
            sys.exit(0) 
            
        elif cmd == "echo":
            # shlex has already removed the quotes from the individual parts
            print(*(parts[1:])) # This is a cleaner way to print space-separated list items
            
        elif cmd == "pwd":
            print(os.getcwd())
            
        elif cmd == "cd":
            if len(parts) > 1:
                # With shlex, parts[1] is already the full path even if it had quotes/spaces
                target_path = os.path.expanduser(parts[1])
                try:
                    os.chdir(target_path)
                except FileNotFoundError:
                    print(f"cd: {target_path}: No such file or directory")
            else:
                os.chdir(os.path.expanduser("~"))
            
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
                pass
                
        else:
            if shutil.which(cmd):
                subprocess.run(parts)
            else:
                print(f"{cmd}: not found")
    


if __name__ == "__main__":
    main()
