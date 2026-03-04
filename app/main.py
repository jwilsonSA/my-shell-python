import sys


def main():
    while True:
        sys.stdout.write("$ ")
        
        # Waitt for user input
        command = input()
        if command == "exit":
            break
        elif command.startswith("echo "):
            print(f"{command} is a shell builtin")
        elif command.startswith("exit"):
            print(f"{command} is a shell builtin")
        else:
            print(f"{command}: command not found")
    


if __name__ == "__main__":
    main()
