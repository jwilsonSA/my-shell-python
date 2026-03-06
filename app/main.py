import sys
import shutil
import subprocess
import os


def main():
    builtins = ["echo", "exit", "type", "pwd", "cd"]
        
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        
        user_input = input().strip()
        
        if not user_input:
            continue
        
        parts = user_input.split()
        cmd = parts[0]
        
        if cmd == "exit":
            sys.exit(0) 
            
        elif cmd == "echo":
            print(" ".join(parts[1:]))
            
        elif cmd == "pwd":
            print(os.getcwd())
            
        elif cmd == "cd":
            path = parts[1] if len(parts) > 1 else "~"
            try:
                os.chdir(os.path.expanduser(path))
            except FileNotFoundError:
                print(f"cd: {path}: No such file or directory")
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
