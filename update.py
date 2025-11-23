import subprocess
import sys
import os

def run_command(command):
    print(f"Running: {command}")
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        sys.exit(1)

def main():
    print("Starting update process...")
    
    # 1. Update code from Git
    print("--- Pulling latest changes from Git ---")
    # Check if git is available and we are in a git repo
    if os.path.exists('.git'):
        run_command("git pull")
    else:
        print("Warning: Not a git repository. Skipping git pull.")
    
    # 2. Install dependencies
    print("--- Installing requirements ---")
    if os.path.exists('requirements.txt'):
        run_command(f"{sys.executable} -m pip install -r requirements.txt")
    else:
        print("Warning: requirements.txt not found.")
    
    # 3. Run database migration
    print("--- Running database migration ---")
    if os.path.exists('migrate.py'):
        run_command(f"{sys.executable} migrate.py")
    else:
        print("Error: migrate.py not found!")
        sys.exit(1)
    
    print("\nUpdate completed successfully!")

if __name__ == "__main__":
    main()
