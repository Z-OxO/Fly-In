import sys

from src.main import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("Bye ;3")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error occured: {e}", file=sys.stderr)
        sys.exit(1)
