import sys
import os

# Ensure the root directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from src.main import main
        main()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
        sys.exit(0)
