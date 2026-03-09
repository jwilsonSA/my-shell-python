import os
import sys
import shutil
import subprocess
import readline

def main():
    builtins = ["echo", "exit", "type", "pwd", "cd"]
        
    ## SECTION: Autocompletion Configuration (Multiple Match Support)
    last_tab_text = [None]
    tab_count = [0]

    def completer(text, state):
        buffer = readline.get_line_buffer()
        if " " in buffer.lstrip():
            return None

        # 1. Gather all unique candidates
        candidates = set(i for i in builtins if i.startswith(text))
        path_env = os.environ.get("PATH", "")
        for directory in path_env.split(":"):
            if os.path.isdir(directory):
                try:
                    for filename in os.listdir(directory):
                        full_path = os.path.join(directory, filename)
                        if filename.startswith(text) and os.access(full_path, os.X_OK):
                            candidates.add(filename)
                except PermissionError:
                    continue
        
        options = sorted(list(candidates))

        # 2. Logic for 0, 1, or Multiple matches
        if not options:
            return None

        if len(options) == 1:
            return options[state] + " " if state < 1 else None

        # 3. Handle Multiple Matches (The Double-Tab Logic)
        if state == 0:
            if buffer == last_tab_text[0]:
                tab_count[0] += 1
            else:
                last_tab_text[0] = buffer
                tab_count[0] = 1

            if tab_count[0] == 1:
                sys.stdout.write("\x07")
                sys.stdout.flush()
            elif tab_count[0] >= 2:
                sys.stdout.write("\n" + "  ".join(options) + "\n")
                sys.stdout.write(f"$ {buffer}")
                sys.stdout.flush()
        
        return None

    readline.set_completer(completer)
    readline.set_completer_delims('\t\n') 
    
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")
    
    ## SECTION: Main Shell Loop
    while True:
        try:
            user_input = input("$ ")
        except EOFError:
            break
            
        if not user_input.strip():
            continue
        
        parts = parse_args(user_input)
        if not parts:
            continue
        
        output_file = None
        error_file = None
        
        ## SECTION: Redirection Parsing
        if "2>>" in parts:
            idx = parts.index("2>>")
            filename = parts[idx + 1]
            os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
            error_file = open(filename, "a")
            parts = parts[:idx] + parts[idx+2:]
        elif "2>" in parts:
            idx = parts.index("2>")
            filename = parts[idx + 1]
            os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
            error_file = open(filename, "w")
            parts = parts[:idx] + parts[idx+2:]
        
        if ">>" in parts or "1>>" in parts:
            idx = parts.index(">>") if ">>" in parts else parts.index("1>>")
            filename = parts[idx + 1]
            os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
            output_file = open(filename, "a")
            parts = parts[:idx] + parts[idx+2:]
        elif ">" in parts or "1>" in parts:
            idx = parts.index(">") if ">" in parts else parts.index("1>")
            filename = parts[idx + 1]
            os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
            output_file = open(filename, "w")
            parts = parts[:idx] + parts[idx+2:]
            
        if not parts: 
            if output_file: output_file.close()
            if error_file: error_file.close()
            continue

        cmd = parts[0]
        t_stdout = output_file if output_file else sys.stdout
        t_stderr = error_file if error_file else sys.stderr
        
        ## SECTION: Builtin Command Execution
        if cmd == "exit":
            if output_file: output_file.close()
            if error_file: error_file.close()
            sys.exit(0) 
            
        elif cmd == "echo":
            print(*(parts[1:]), file=t_stdout)
            t_stdout.flush()
            
        elif cmd == "pwd":
            print(os.getcwd(), file=t_stdout)
            t_stdout.flush()
            
        elif cmd == "cd":
            if len(parts) > 1:
                target_path = os.path.expanduser(parts[1])
                try:
                    os.chdir(target_path)
                except FileNotFoundError:
                    t_stderr.write(f"cd: {target_path}: No such file or directory\n")
                    t_stderr.flush()
            else:
                os.chdir(os.path.expanduser("~"))
            
        elif cmd == "type":
            if len(parts) > 1:
                target = parts[1]
                msg = ""
                if target in builtins:
                    msg = f"{target} is a shell builtin\n"
                elif path := shutil.which(target):
                    msg = f"{target} is {path}\n"
                else:
                    msg = f"{target}: not found\n"
                t_stdout.write(msg)
                t_stdout.flush()
                
        ## SECTION: External Command Execution
        else:
            if shutil.which(cmd):
                subprocess.run(parts, stdout=t_stdout, stderr=t_stderr)
            else:
                t_stderr.write(f"{cmd}: not found\n")
                t_stderr.flush()
        
        ## SECTION: Cleanup and File Syncing
        if output_file:
            output_file.flush()
            os.fsync(output_file.fileno()) 
            output_file.close()
        if error_file:
            error_file.flush()
            os.fsync(error_file.fileno())
            error_file.close()
    
## SECTION: Argument Parsing and Quoting Logic
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