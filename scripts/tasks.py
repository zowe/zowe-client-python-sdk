import os
import shutil
import sys
import webbrowser


def doc_open():
    """Opens the generated docs in a web browser."""
    path = "docs/build/html/index.html"
    print(f"Opening {path} in web browser...")
    abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path)
    webbrowser.open("file://" + abs_path.replace("\\", "/"))


def env_active():
    """Prints the virtual environment activation instructions."""
    activate_cmd = "env\\Scripts\\activate" if sys.platform == "win32" else "source env/bin/activate"
    print(f"To activate, run the following command:\n\n{activate_cmd}\n\nTo deactivate, simply run:\n\ndeactivate\n")


def env_delete():
    """Deletes the 'env' directory."""
    print("Deleting virtual environment 'env'...")
    shutil.rmtree("env", ignore_errors=True)
    print("'env' deleted.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tasks.py [doc-open|env-active|env-delete]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "doc-open":
        doc_open()
    elif command == "env-active":
        env_active()
    elif command == "env-delete":
        env_delete()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
