from src.app import init_app
from src.cli import repl

def main():
    init_app()
    repl()

if __name__ == "__main__":
    main()