import os
import sys, shutil, shlex, subprocess


def main():
    builtins = ["echo", "exit", "type", "pwd", "cd"]
        
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        
        try:
            user_input = input()
        except EOFError:
            break
            
        if not user_input.strip():
            continue
        
        try:
            parts = shlex.split(user_input, posix=True)
        except ValueError as e:
            print(f"shell: {e}")
            continue

        if not parts:
            continue

        cmd = parts[0]
        
        if cmd == "exit":
            sys.exit(0) 
            
        elif cmd == "echo":
            print(*(parts[1:]))
            
        elif cmd == "pwd":
            print(os.getcwd())
            
        elif cmd == "cd":
            if len(parts) > 1:
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
    

def parse_args(input_str):
    args = []
    current = []
    escaped = False
    quote = None  # Tracks if we are in ' or "

    for i, char in enumerate(input_str):
        if escaped:
            current.append(char)
            escaped = False
            continue

        if char == '\\':
            # In POSIX, \ inside "" only escapes specific chars ($, `, ", \, \n)
            # Outside quotes, it escapes everything.
            if quote == "'":
                current.append(char)
            else:
                escaped = True
            continue

        if char in ("'", '"'):
            if quote == char:
                quote = None # Closing quote
            elif quote is None:
                quote = char # Opening quote
            else:
                current.append(char) # Inside the other type of quote
            continue

        if char == ' ' and quote is None:
            if current:
                args.append("".join(current))
                current = []
            continue

        current.append(char)

    if current:
        args.append("".join(current))
    return args

if __name__ == "__main__":
    main()
