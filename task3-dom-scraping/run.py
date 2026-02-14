import os
import sys
import subprocess

def main():
    """
    Entrypoint to run the Task 3 scraper.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "src", "scraper.py")
    
    # Forward arguments appropriately
    args = [sys.executable, script_path] + sys.argv[1:]
    
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing scraper: {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
