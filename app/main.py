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
        
        parts = parse_args(user_input)
        if not parts:
            continue
        
        output_file = None
        
        if ">" in parts or "1>" in parts:
            try:
                idx = parts.index(">") if ">" in parts else parts.index("1>")
                
                filename = parts[idx + 1]
                output_file = open(filename, "w")
                
                parts = parts[:idx] + parts[idx+2:]
            except IndexError:
                print("shell: syntax error near unexpected token `newline'")
                continue
            
        cmd = parts[0]
        
        target_stdout = output_file if output_file else sys.stdout 
        
        if cmd == "exit":
            if output_file: output_file.close()
            sys.exit(0) 
            
        elif cmd == "echo":
            print(*(parts[1:]), file=target_stdout)
            
        elif cmd == "pwd":
            print(os.getcwd(), file=target_stdout)
            
        elif cmd == "cd":
            if len(parts) > 1:
                target_path = os.path.expanduser(parts[1])
                try:
                    os.chdir(target_path)
                except FileNotFoundError:
                    sys.stderr.write(f"cd: {target_path}: No such file or directory\n")
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
                subprocess.run(parts, stdout=target_stdout)
            else:
                print(f"{cmd}: not found")
                
        if output_file:
            output_file.close()
    

def parse_args(input_str):
    args = []
    current = []
    escaped = False
    quote = None 

    i = 0
    while i < len(input_str):
        char = input_str[i]

        if escaped:
            current.append(char)
            escaped = False
        elif quote == "'":
            if char == "'":
                quote = None
            else:
                current.append(char)
        elif quote == '"':
            if char == '\\':
                if i + 1 < len(input_str) and input_str[i+1] in ('$', '`', '"', '\\', '\n'):
                    escaped = True
                else:
                    current.append(char)
            elif char == '"':
                quote = None
            else:
                current.append(char)
        else:
            if char == '\\':
                escaped = True
            elif char in ("'", '"'):
                quote = char
            elif char == ' ':
                if current:
                    args.append("".join(current))
                    current = []
            else:
                current.append(char)
        i += 1

    if current:
        args.append("".join(current))
    return args

if __name__ == "__main__":
    main()
