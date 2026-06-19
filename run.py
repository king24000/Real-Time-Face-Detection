import os
import sys
import uvicorn

# Ensure the root directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from src.config import HOST, PORT
        print(f"\n==============================================")
        print(f"   Launch URL: http://localhost:{PORT}        ")
        print(f"==============================================\n")
        uvicorn.run("src.main:app", host=HOST, port=PORT, reload=True)
    except KeyboardInterrupt:
        print("\nServer shutdown complete.")
        sys.exit(0)
