import os
import sys, shutil, shlex, subprocess


def main():
    builtins = ["echo", "exit", "type", "pwd", "cd"]
        
    while True:
        # 1. Always flush the prompt
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
        error_file = None
        
        # --- Redirection Logic ---
        if "2>" in parts:
            idx = parts.index("2>")
            filename = parts[idx + 1]
            parent_dir = os.path.dirname(filename)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            error_file = open(filename, "w")
            parts = parts[:idx] + parts[idx+2:]
        
        if ">" in parts or "1>" in parts:
            idx = parts.index(">") if ">" in parts else parts.index("1>")
            filename = parts[idx + 1]
            parent_dir = os.path.dirname(filename)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            output_file = open(filename, "w")
            parts = parts[:idx] + parts[idx+2:]
            
        # If redirection stripped everything, clean up and go back to prompt
        if not parts: 
            if output_file: output_file.close()
            if error_file: error_file.close()
            continue

        cmd = parts[0]
        t_stdout = output_file if output_file else sys.stdout
        t_stderr = error_file if error_file else sys.stderr
        
        # --- Command Execution ---
        if cmd == "exit":
            if output_file: output_file.close()
            if error_file: error_file.close()
            sys.exit(0) 
            
        elif cmd == "echo":
            print(*(parts[1:]), file=t_stdout)
            t_stdout.flush() # Ensure it's written
            
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
                
        else:
            if shutil.which(cmd):
                # Subprocess handles its own flushing on completion
                subprocess.run(parts, stdout=t_stdout, stderr=t_stderr)
            else:
                t_stderr.write(f"{cmd}: not found\n")
                t_stderr.flush()
        
        # --- Cleanup ---
        if output_file:
            output_file.flush()
            os.fsync(output_file.fileno()) # Force write to disk
            output_file.close()
        if error_file:
            error_file.flush()
            os.fsync(error_file.fileno()) # Force write to disk
            error_file.close()
    

def parse_args(input_str):
    args = []
    current = []
    escaped = False
    quote = None 

    i = 0
    while i < len(input_str):
        char