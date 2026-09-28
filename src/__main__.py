import sys

from src.main import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unexpected error occured: {e}")
    except KeyboardInterrupt:
        print("Bye ;3")
